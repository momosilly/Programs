package com.example.healthcoach

import android.os.Bundle
import android.util.Log
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import android.widget.ImageButton
import android.widget.LinearLayout
import androidx.activity.result.ActivityResultLauncher
import androidx.appcompat.app.AppCompatActivity
import androidx.cardview.widget.CardView
import androidx.health.connect.client.HealthConnectClient
import androidx.health.connect.client.PermissionController
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.launch
import java.time.Duration
import java.time.Instant
import android.content.Intent
import android.net.Uri
import android.provider.Settings
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import java.io.IOException
import android.view.View
import android.view.inputmethod.InputMethodManager
import android.content.Context
import android.os.Build

class MainActivity : AppCompatActivity() {

    private lateinit var repo: HealthRepository
    private lateinit var healthConnectClient: HealthConnectClient
    private lateinit var statusText: TextView
    private lateinit var requestButton: Button
    private lateinit var openSettingsButton: Button
    private lateinit var sendButton: Button
    private lateinit var inputField: EditText
    private lateinit var requestPermissionLauncher: ActivityResultLauncher<Set<String>>

    private lateinit var loadingLayout: LinearLayout
    private lateinit var loadingText: TextView
    private lateinit var responseCard: CardView
    private lateinit var geminiResponseText: TextView
    private lateinit var closeButton: ImageButton

    private val serverUrl = "https://health-coach-q3av.onrender.com//healthdata"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Initialize views
        statusText = findViewById(R.id.statusText)
        requestButton = findViewById(R.id.requestPermissionsButton)
        openSettingsButton = findViewById(R.id.openHealthConnectButton)
        sendButton = findViewById(R.id.sendButton)
        inputField = findViewById(R.id.userInputField)
        loadingLayout = findViewById(R.id.loadingLayout)
        loadingText = findViewById(R.id.loadingText)
        responseCard = findViewById(R.id.responseCard)
        geminiResponseText = findViewById(R.id.geminiResponseText)
        closeButton = findViewById(R.id.closeButton)

        // Check Android version (API 34 = Android 14)
        val androidVersion = Build.VERSION.SDK_INT
        val isAndroid14Plus = androidVersion >= 34  // Android 14 = API 34

        Log.d("HC", "Android API Level: $androidVersion")

        // Try to get the correct provider package name
        val availablePackages = HealthConnectClient.getHealthConnectManageDataIntent(this)
        Log.d("HC", "Health Connect action: $availablePackages")

        // Determine package name based on Android version
        val packageName = if (isAndroid14Plus) {
            "com.android.healthconnect.controller" // Android 14+ built-in
        } else {
            "com.google.android.apps.healthdata" // Android 13 and below
        }

        val sdkStatus = HealthConnectClient.getSdkStatus(this, packageName)

        Log.d("HC", "Using package: $packageName")
        Log.d("HC", "SDK Status: $sdkStatus")
        Log.d("HC", "SDK_AVAILABLE constant: ${HealthConnectClient.SDK_AVAILABLE}")

        if (sdkStatus != HealthConnectClient.SDK_AVAILABLE) {
            statusText.text = "❌ Health Connect not available"
            requestButton.isEnabled = false
            sendButton.isEnabled = false

            if (isAndroid14Plus) {
                // Android 14+: Health Connect is built-in
                openSettingsButton.text = "Open Health Settings"
                openSettingsButton.setOnClickListener {
                    try {
                        val intent = Intent("android.health.connect.action.MANAGE_HEALTH_DATA")
                        startActivity(intent)
                    } catch (e: Exception) {
                        Log.e("HC", "Failed to open Health Connect settings", e)
                        try {
                            // Fallback: Try direct package intent
                            val fallbackIntent = Intent().apply {
                                action = Intent.ACTION_MAIN
                                setPackage("com.android.healthconnect.controller")
                            }
                            startActivity(fallbackIntent)
                        } catch (e2: Exception) {
                            Log.e("HC", "Fallback also failed", e2)
                            // Last resort: general settings
                            startActivity(Intent(Settings.ACTION_SETTINGS))
                        }
                    }
                }
            } else {
                // Android 13 and below: Need separate app
                openSettingsButton.text = "Install Health Connect"
                openSettingsButton.setOnClickListener {
                    val intent = Intent(Intent.ACTION_VIEW).apply {
                        data = Uri.parse("https://play.google.com/store/apps/details?id=com.google.android.apps.healthdata")
                        setPackage("com.android.vending")
                    }
                    startActivity(intent)
                }
            }
            return
        }

        // Initialize Health Connect
        healthConnectClient = HealthConnectClient.getOrCreate(this)
        repo = HealthRepository(this)

        // Set up permission launcher
        requestPermissionLauncher = registerForActivityResult(
            PermissionController.createRequestPermissionResultContract()
        ) { grantedPermissions ->
            lifecycleScope.launch {
                updatePermissionStatus()
            }
        }

        // Request Permissions button
        requestButton.setOnClickListener {
            lifecycleScope.launch {
                try {
                    val granted = repo.getGrantedPermissions()
                    val needed = repo.requiredPermissions() - granted

                    if (needed.isNotEmpty()) {
                        statusText.text = "🔄 Requesting ${needed.size} permissions..."
                        requestPermissionLauncher.launch(needed)
                    } else {
                        statusText.text = "✅ All permissions granted!"
                    }
                } catch (e: Exception) {
                    Log.e("HC", "Error requesting permissions", e)
                    e.printStackTrace()
                    statusText.text = "❌ Error: ${e.message}"
                }
            }
        }

        // Open Health Connect button
        openSettingsButton.setOnClickListener {
            try {
                if (isAndroid14Plus) {
                    // Android 14+: Use the action from getHealthConnectManageDataAction
                    val intent = Intent("android.health.connect.action.MANAGE_HEALTH_DATA")
                    startActivity(intent)
                    statusText.text = "📱 Opening Health Connect Settings..."
                } else {
                    // Android 13 and below: Open Health Connect app
                    val intent = packageManager.getLaunchIntentForPackage(packageName)
                    if (intent != null) {
                        startActivity(intent)
                        statusText.text = "📱 Opening Health Connect..."
                    } else {
                        val settingsIntent = Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS).apply {
                            data = Uri.fromParts("package", packageName, null)
                        }
                        startActivity(settingsIntent)
                    }
                }
            } catch (e: Exception) {
                Log.e("HC", "Error opening Health Connect", e)
                e.printStackTrace()
                statusText.text = "❌ Could not open Health Connect: ${e.message}"
            }
        }

        // Send button
        sendButton.setOnClickListener {
            val userInput = inputField.text.toString().trim()

            // Hide keyboard
            val imm = getSystemService(INPUT_METHOD_SERVICE) as InputMethodManager
            imm.hideSoftInputFromWindow(inputField.windowToken, 0)

            lifecycleScope.launch {
                showLoading(true)
                responseCard.visibility = View.GONE

                try {
                    collectAndSendData(userInput)
                } catch (e: Exception) {
                    Log.e("HC", "Error collecting data", e)
                    e.printStackTrace()
                    showLoading(false)
                    showError("Failed to collect health data: ${e.message}")
                }
            }
        }

        // Close button
        closeButton.setOnClickListener {
            responseCard.visibility = View.GONE
            inputField.text.clear()
        }

        // Initial permission check
        lifecycleScope.launch {
            updatePermissionStatus()
        }
    }

    private suspend fun updatePermissionStatus() {
        try {
            val granted = repo.getGrantedPermissions()
            val total = repo.requiredPermissions().size

            val percentage = (granted.size * 100) / total
            val emoji = when {
                granted.size == total -> "✅"
                granted.size > 0 -> "⚠️"
                else -> "❌"
            }

            statusText.text = "$emoji Permissions: ${granted.size}/$total granted ($percentage%)"

            // Enable/disable send button based on permissions
            sendButton.isEnabled = granted.isNotEmpty()

            if (granted.isEmpty()) {
                statusText.text = "❌ No permissions granted. Please grant at least one permission."
            }
        } catch (e: Exception) {
            statusText.text = "❌ Error checking permissions. Please make sure that Health Connect is installed."
            Log.e("HC", "Error updating status", e)
        }
    }

    private fun showLoading(show: Boolean) {
        loadingLayout.visibility = if (show) View.VISIBLE else View.GONE
        sendButton.isEnabled = !show
        requestButton.isEnabled = !show
        openSettingsButton.isEnabled = !show
    }

    private fun showError(message: String) {
        runOnUiThread {
            responseCard.visibility = View.VISIBLE
            geminiResponseText.text = "❌ Error: $message"
        }
    }

    private suspend fun collectAndSendData(userInput: String) {
        loadingText.text = "📊 Collecting health data..."

        val steps = repo.getStepsLast24Hours()
        val (hrMin, hrMax) = repo.getHeartRateMinMaxLast24Hours()
        val restingHr = repo.getRestingHeartRateLast24Hours()
        val totalCalories = repo.getTotalCaloriesLast24Hours()
        val sleepSessions = repo.getSleepSessionsLast24Hours()
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
                val durationMinutes = Duration.between(stage.startTime, stage.endTime).toMinutes()
                mapOf(
                    "type" to stageName,
                    "type_code" to stage.stage,
                    "start" to stage.startTime.toString(),
                    "end" to stage.endTime.toString(),
                    "duration_minutes" to durationMinutes
                )
            }
        }

        val exerciseSessions = repo.getExerciseSessionsLast24Hours()
        val exerciseDuration = exerciseSessions.sumOf { it.durationMinutes }
        val granted = repo.getGrantedPermissions()
        val required = repo.requiredPermissions()

        loadingText.text = "🤖 Analyzing with AI..."

        val payload = mapOf(
            "timestamp" to Instant.now().toString(),
            "user_note" to userInput,
            "steps_last_24h" to steps,
            "heart_rate_min" to hrMin,
            "heart_rate_max" to hrMax,
            "total_calories_burned" to totalCalories,
            "resting_heart_rate" to restingHr,
            "sleep_hours" to sleepHours,
            "sleep_sessions" to sleepSessions.map {
                mapOf(
                    "start" to it.startTime.toString(),
                    "end" to it.endTime.toString(),
                    "title" to (it.title ?: "Sleep"),
                    "notes" to (it.notes ?: "")
                )
            },
            "sleep_stages" to sleepStages,
            "exercise_duration_minutes" to exerciseDuration,
            "exercise_sessions" to exerciseSessions.map {
                mapOf(
                    "type" to it.type,
                    "duration_minutes" to it.durationMinutes,
                    "title" to it.title
                )
            },
            "permissions_granted" to granted.size,
            "permissions_total" to required.size
        )

        sendToBackend(payload)
    }

    private fun sendToBackend(payload: Map<String, Any>) {
        val json = JSONObject(payload).toString()

// Increase timeouts for Gemini API (can take 30-60 seconds)
        val client = OkHttpClient.Builder()
            .connectTimeout(30, java.util.concurrent.TimeUnit.SECONDS)
            .readTimeout(60, java.util.concurrent.TimeUnit.SECONDS)  // Important for Gemini!
            .writeTimeout(30, java.util.concurrent.TimeUnit.SECONDS)
            .build()

        val requestBody = json.toRequestBody("application/json".toMediaType())
        val request = Request.Builder()
            .url(serverUrl)
            .post(requestBody)
            .build()

        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                Log.e("HC", "❌ Failed to send data", e)
                runOnUiThread {
                    showLoading(false)
                    showError("Network error: ${e.message}")
                }
            }

            override fun onResponse(call: Call, response: Response) {
                val body = response.body?.string()

                runOnUiThread {
                    showLoading(false)

                    if (!response.isSuccessful) {
                        showError("Server error: ${response.code}")
                        return@runOnUiThread
                    }

                    if (body != null) {
                        try {
                            val json = JSONObject(body)
                            val data = json.getJSONObject("data_received")
                            val insight = data.optString("gemini_insight", "")

                            if (insight.isNotEmpty()) {
                                // Convert Markdown bold (**text**) to HTML
                                var htmlText = insight

                                // Replace **bold** with <b>bold</b>
                                val boldPattern = """\*\*(.+?)\*\*""".toRegex()
                                htmlText = boldPattern.replace(htmlText) { "<b>${it.groupValues[1]}</b>" }

                                // Replace *italic* with <i>italic</i>
                                val italicPattern = """\*(.+?)\*""".toRegex()
                                htmlText = italicPattern.replace(htmlText) { "<i>${it.groupValues[1]}</i>" }

                                // Replace newlines with <br>
                                htmlText = htmlText.replace("\n", "<br>")

                                // Render HTML
                                geminiResponseText.text = if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.N) {
                                    android.text.Html.fromHtml(htmlText, android.text.Html.FROM_HTML_MODE_LEGACY)
                                } else {
                                    @Suppress("DEPRECATION")
                                    android.text.Html.fromHtml(htmlText)
                                }

                                responseCard.visibility = View.VISIBLE

                                // Scroll to show the response
                                responseCard.postDelayed({
                                    responseCard.requestFocus()
                                }, 100)
                            } else {
                                showError("No insight received from server")
                            }
                        } catch (e: Exception) {
                            Log.e("HC", "❌ Failed to parse response", e)
                            showError("Failed to parse response: ${e.message}")
                        }
                    } else {
                        showError("Empty response from server")
                    }
                }
            }
        })
    }

    override fun onResume() {
        super.onResume()
        lifecycleScope.launch {
            updatePermissionStatus()
        }
    }
}
