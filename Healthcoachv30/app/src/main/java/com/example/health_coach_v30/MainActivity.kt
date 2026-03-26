package com.example.healthcoach

import android.os.Build
import android.os.Bundle
import android.util.Log
import androidx.appcompat.app.AppCompatActivity
import androidx.activity.result.ActivityResultLauncher
import androidx.health.connect.client.HealthConnectClient
import androidx.health.connect.client.PermissionController
import androidx.lifecycle.lifecycleScope
import com.example.health_coach_v30.HealthRepository
import kotlinx.coroutines.launch

class MainActivity : AppCompatActivity() {

    companion object {
        private const val TAG        = "HealthCoach"
        private const val SERVER_PORT = 8080
    }

    private lateinit var repo: HealthRepository
    private lateinit var server: HealthServer
    private lateinit var requestPermissionLauncher: ActivityResultLauncher<Set<String>>

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // No setContentView — this activity has no UI.
        // React Native runs in a separate process and talks to the server on localhost.

        val isAndroid14Plus = Build.VERSION.SDK_INT >= 34
        val packageName = if (isAndroid14Plus) {
            "com.android.healthconnect.controller"
        } else {
            "com.google.android.apps.healthdata"
        }

        val sdkStatus = HealthConnectClient.getSdkStatus(this, packageName)
        if (sdkStatus != HealthConnectClient.SDK_AVAILABLE) {
            Log.e(TAG, "Health Connect not available (status=$sdkStatus). Server will not start.")
            return
        }

        // Initialise repository
        repo = HealthRepository(this)

        // Register permission launcher and request any missing permissions immediately
        requestPermissionLauncher = registerForActivityResult(
            PermissionController.createRequestPermissionResultContract()
        ) { granted ->
            Log.d(TAG, "Permissions granted: ${granted.size}")
        }

        lifecycleScope.launch {
            val granted = repo.getGrantedPermissions()
            val needed  = repo.requiredPermissions() - granted
            if (needed.isNotEmpty()) {
                Log.d(TAG, "Requesting ${needed.size} missing permissions")
                requestPermissionLauncher.launch(needed)
            } else {
                Log.d(TAG, "All permissions already granted")
            }
        }

        // Start the local HTTP server
        startServer()
    }

    private fun startServer() {
        try {
            server = HealthServer(applicationContext, repo, SERVER_PORT)
            server.start()
            Log.d(TAG, "HealthServer running on port $SERVER_PORT")
        } catch (e: Exception) {
            Log.e(TAG, "Failed to start HealthServer", e)
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        if (::server.isInitialized && server.isAlive) {
            server.stop()
            Log.d(TAG, "HealthServer stopped")
        }
    }
}