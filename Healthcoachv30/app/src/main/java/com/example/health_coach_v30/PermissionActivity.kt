package com.example.healthcoach

import android.content.Intent
import android.os.Build
import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.Button
import android.widget.ProgressBar
import android.widget.TextView
import androidx.activity.result.ActivityResultLauncher
import androidx.appcompat.app.AppCompatActivity
import androidx.health.connect.client.HealthConnectClient
import androidx.health.connect.client.PermissionController
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

class PermissionActivity : AppCompatActivity() {

    companion object {
        private const val TAG = "PermissionActivity"
    }

    private lateinit var repo: HealthRepository
    private lateinit var statusText: TextView
    private lateinit var subText: TextView
    private lateinit var progressBar: ProgressBar
    private lateinit var retryButton: Button

    private lateinit var requestPermissionLauncher: ActivityResultLauncher<Set<String>>

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_permission)

        statusText  = findViewById(R.id.statusText)
        subText     = findViewById(R.id.subText)
        progressBar = findViewById(R.id.progressBar)
        retryButton = findViewById(R.id.retryButton)

        retryButton.setOnClickListener {
            retryButton.visibility = View.GONE
            lifecycleScope.launch { checkAndProceed() }
        }

        // Register permission launcher
        requestPermissionLauncher = registerForActivityResult(
            PermissionController.createRequestPermissionResultContract()
        ) { granted ->
            Log.d(TAG, "Permission result: ${granted.size} granted")
            lifecycleScope.launch { checkAndProceed() }
        }

        lifecycleScope.launch { checkAndProceed() }
    }

    private suspend fun checkAndProceed() {
        // ── 1. Check Health Connect availability ─────────────────────────────
        val isAndroid14Plus = Build.VERSION.SDK_INT >= 34
        val packageName = if (isAndroid14Plus) {
            "com.android.healthconnect.controller"
        } else {
            "com.google.android.apps.healthdata"
        }

        val sdkStatus = HealthConnectClient.getSdkStatus(this, packageName)
        if (sdkStatus != HealthConnectClient.SDK_AVAILABLE) {
            showError("Health Connect is not available on this device.")
            return
        }

        // ── 2. Initialise repo ───────────────────────────────────────────────
        if (!::repo.isInitialized) {
            repo = HealthRepository(this)
        }

        // ── 3. Check permissions ─────────────────────────────────────────────
        setStatus("Checking permissions…", showProgress = true)

        val granted = repo.getGrantedPermissions()
        val needed  = repo.requiredPermissions() - granted

        if (needed.isNotEmpty()) {
            setStatus(
                "Permissions needed",
                sub = "${needed.size} Health Connect permission(s) required to continue.",
                showProgress = false
            )
            // Small delay so the user reads the message before the dialog appears
            delay(600)
            requestPermissionLauncher.launch(needed)
            return  // resume in launcher callback → checkAndProceed()
        }

        // ── 4. All permissions granted — start server ────────────────────────
        setStatus("Starting health server…", showProgress = true)

        try {
            HealthServerManager.start(applicationContext, repo)
            Log.d(TAG, "Server started on port ${HealthServerManager.PORT}")
        } catch (e: Exception) {
            Log.e(TAG, "Server start failed", e)
            showError("Could not start health server: ${e.message}")
            return
        }

        // ── 5. Hand off to React Native ──────────────────────────────────────
        setStatus("Ready!", sub = "Loading app…", showProgress = true)
        delay(400)  // brief moment so "Ready!" is visible

        startActivity(Intent(this, MainActivity::class.java))
        finish()  // remove PermissionActivity from the back stack
    }

    // ── UI helpers ────────────────────────────────────────────────────────────

    private fun setStatus(
        status: String,
        sub: String = "",
        showProgress: Boolean = false
    ) {
        runOnUiThread {
            statusText.text  = status
            subText.text     = sub
            subText.visibility   = if (sub.isNotEmpty()) View.VISIBLE else View.GONE
            progressBar.visibility = if (showProgress) View.VISIBLE else View.GONE
            retryButton.visibility = View.GONE
        }
    }

    private fun showError(message: String) {
        runOnUiThread {
            statusText.text  = "Something went wrong"
            subText.text     = message
            subText.visibility   = View.VISIBLE
            progressBar.visibility = View.GONE
            retryButton.visibility = View.VISIBLE
        }
    }
}