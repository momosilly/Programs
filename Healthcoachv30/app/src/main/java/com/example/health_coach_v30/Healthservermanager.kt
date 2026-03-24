package com.example.healthcoach

import android.content.Context
import android.util.Log

/**
 * Singleton that owns the [HealthServer] instance.
 *
 * Using a singleton means:
 *  - The server is started once from PermissionActivity and keeps running.
 *  - MainActivity (RN) never needs to touch it.
 *  - If PermissionActivity is recreated (e.g. rotation), start() is a no-op.
 */
object HealthServerManager {

    private const val TAG = "HealthServerManager"
    const val PORT = 8080

    @Volatile
    private var server: HealthServer? = null

    /** Start the server. Safe to call multiple times — only starts once. */
    fun start(context: Context, repo: HealthRepository) {
        if (server?.isAlive == true) {
            Log.d(TAG, "Server already running on port $PORT")
            return
        }
        val s = HealthServer(context.applicationContext, repo, PORT)
        s.start()
        server = s
        Log.d(TAG, "Server started on port $PORT")
    }

    /** Stop the server (call from Application.onTerminate or a shutdown hook). */
    fun stop() {
        server?.let {
            if (it.isAlive) {
                it.stop()
                Log.d(TAG, "Server stopped")
            }
        }
        server = null
    }

    val isRunning: Boolean get() = server?.isAlive == true
}