package com.example.healthcoach

import android.content.Context
import android.util.Log
import fi.iki.elonen.NanoHTTPD
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking
import org.json.JSONObject
import java.time.Duration
import java.time.Instant

class HealthServer(
    private val context: Context,
    private val repo: HealthRepository,
    port: Int = 8080
) : NanoHTTPD(port) {

    companion object {
        private const val TAG = "HealthServer"
        private const val BACKEND_URL = "https://health-coach-q3av.onrender.com//healthdata"
    }

    override fun serve(session: IHTTPSession): Response {
        val method = session.method
        val uri = session.uri

        Log.d(TAG, "Incoming: $method $uri")

        // ── CORS pre-flight ──────────────────────────────────────────────────
        if (method == Method.OPTIONS) {
            return corsResponse(newFixedLengthResponse(""))
        }

        return when {
            uri == "/healthdata" && method == Method.POST -> handleHealthData(session)
            uri == "/ping"       && method == Method.GET  -> handlePing()
            else -> corsResponse(
                newFixedLengthResponse(
                    Response.Status.NOT_FOUND,
                    "application/json",
                    """{"error":"Not found"}"""
                )
            )
        }
    }

    // ── GET /ping ────────────────────────────────────────────────────────────
    private fun handlePing(): Response =
        corsResponse(
            newFixedLengthResponse(
                Response.Status.OK,
                "application/json",
                """{"status":"ok"}"""
            )
        )

    // ── POST /healthdata ─────────────────────────────────────────────────────
    private fun handleHealthData(session: IHTTPSession): Response {
        // 1. Parse request body
        val userNote = try {
            val contentLength = session.headers["content-length"]?.toIntOrNull() ?: 0
            val bodyBytes = ByteArray(contentLength)
            session.inputStream.read(bodyBytes, 0, contentLength)
            val bodyStr = String(bodyBytes, Charsets.UTF_8)
            if (bodyStr.isNotBlank()) {
                JSONObject(bodyStr).optString("user_note", "")
            } else {
                ""
            }
        } catch (e: Exception) {
            Log.w(TAG, "Could not parse body: ${e.message}")
            ""
        }

        // 2. Collect health data (blocking — NanoHTTPD runs on its own thread pool)
        val payload: Map<String, Any> = try {
            runBlocking { collectHealthData(userNote) }
        } catch (e: Exception) {
            Log.e(TAG, "Health data collection failed", e)
            return corsResponse(
                newFixedLengthResponse(
                    Response.Status.INTERNAL_ERROR,
                    "application/json",
                    """{"error":"Health data collection failed: ${e.message}"}"""
                )
            )
        }

        // 3. Forward to render.com backend and return its response verbatim
        return try {
            val backendResponse = forwardToBackend(payload)
            corsResponse(
                newFixedLengthResponse(
                    Response.Status.OK,
                    "application/json",
                    backendResponse
                )
            )
        } catch (e: Exception) {
            Log.e(TAG, "Backend request failed", e)
            corsResponse(
                newFixedLengthResponse(
                    Response.Status.INTERNAL_ERROR,
                    "application/json",
                    """{"error":"Backend request failed: ${e.message}"}"""
                )
            )
        }
    }

    // ── Collect all health data from Health Connect ──────────────────────────
    private suspend fun collectHealthData(userNote: String): Map<String, Any> {
        val steps          = repo.getStepsLast24Hours()
        val (hrMin, hrMax) = repo.getHeartRateMinMaxLast24Hours()
        val restingHr      = repo.getRestingHeartRateLast24Hours()
        val totalCalories  = repo.getTotalCaloriesLast24Hours()
        val sleepSessions  = repo.getSleepSessionsLast24Hours()
        val exerciseSessions = repo.getExerciseSessionsLast24Hours()

        val sleepHours = sleepSessions.sumOf {
            Duration.between(it.startTime, it.endTime).toMinutes()
        } / 60.0

        val sleepStages = sleepSessions.flatMap { session ->
            session.stages.map { stage ->
                val stageName = when (stage.stage) {
                    1 -> "AWAKE"
                    2 -> "SLEEPING"
                    3 -> "OUT_OF_BED"
                    4 -> "LIGHT"
                    5 -> "DEEP"
                    6 -> "REM"
                    else -> "UNKNOWN"
                }
                mapOf(
                    "type"             to stageName,
                    "type_code"        to stage.stage,
                    "start"            to stage.startTime.toString(),
                    "end"              to stage.endTime.toString(),
                    "duration_minutes" to Duration.between(stage.startTime, stage.endTime).toMinutes()
                )
            }
        }

        val granted  = repo.getGrantedPermissions()
        val required = repo.requiredPermissions()

        return mapOf(
            "timestamp"                  to Instant.now().toString(),
            "user_note"                  to userNote,
            "steps_last_24h"             to steps,
            "heart_rate_min"             to hrMin,
            "heart_rate_max"             to hrMax,
            "total_calories_burned"      to totalCalories,
            "resting_heart_rate"         to restingHr,
            "sleep_hours"                to sleepHours,
            "sleep_sessions"             to sleepSessions.map {
                mapOf(
                    "start" to it.startTime.toString(),
                    "end"   to it.endTime.toString(),
                    "title" to (it.title ?: "Sleep"),
                    "notes" to (it.notes ?: "")
                )
            },
            "sleep_stages"               to sleepStages,
            "exercise_duration_minutes"  to exerciseSessions.sumOf { it.durationMinutes },
            "exercise_sessions"          to exerciseSessions.map {
                mapOf(
                    "type"             to it.type,
                    "duration_minutes" to it.durationMinutes,
                    "title"            to it.title
                )
            },
            "permissions_granted"        to granted.size,
            "permissions_total"          to required.size
        )
    }

    // ── Forward payload to render.com and return raw response body ────────────
    private fun forwardToBackend(payload: Map<String, Any>): String {
        val responseHolder = arrayOf<String?>(null)
        val errorHolder    = arrayOf<Exception?>(null)

        NetworkClient.postJson(BACKEND_URL, payload) { success, body ->
            if (success) {
                responseHolder[0] = body
            } else {
                errorHolder[0] = Exception(body ?: "Unknown backend error")
            }
        }

        // NetworkClient.postJson is async; spin-wait is fine here because
        // NanoHTTPD's serve() already runs off the main thread.
        val deadline = System.currentTimeMillis() + 90_000  // 90 s timeout
        while (responseHolder[0] == null && errorHolder[0] == null) {
            if (System.currentTimeMillis() > deadline) {
                throw Exception("Backend request timed out")
            }
            Thread.sleep(50)
        }

        errorHolder[0]?.let { throw it }
        return responseHolder[0] ?: throw Exception("Empty backend response")
    }

    // ── Add CORS headers to any response ────────────────────────────────────
    private fun corsResponse(response: Response): Response {
        response.addHeader("Access-Control-Allow-Origin",  "*")
        response.addHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        response.addHeader("Access-Control-Allow-Headers", "Content-Type")
        return response
    }
}