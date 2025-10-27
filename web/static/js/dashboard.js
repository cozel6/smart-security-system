/**
 * Smart Security System - Dashboard JavaScript
 *
 * Handles:
 * - Real-time status updates
 * - Arm/Disarm controls
 * - System metrics display
 * - Detection history
 */

// ==========================================
// Configuration
// ==========================================

const CONFIG = {
    updateInterval: 2000,  // Update status every 2 seconds
    apiBaseUrl: '',  // Empty = same origin
};

// ==========================================
// State Management
// ==========================================

let updateTimer = null;
let currentState = 'unknown';

// ==========================================
// Initialization
// ==========================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard initializing...');

    // TODO: Initialize dashboard
    initializeDashboard();

    // TODO: Start periodic updates
    startPeriodicUpdates();

    // TODO: Setup event listeners
    setupEventListeners();

    console.log('Dashboard ready!');
});

// ==========================================
// Initialization Functions
// ==========================================

function initializeDashboard() {
    /**
     * Initialize dashboard components
     *
     * TODO:
     * - Fetch initial status
     * - Update UI elements
     * - Setup clock
     */

    // Update current time
    updateClock();
    setInterval(updateClock, 1000);

    // Fetch initial status
    fetchSystemStatus();
}

function setupEventListeners() {
    /**
     * Setup event listeners for buttons and controls
     *
     * TODO:
     * - Arm button click
     * - Disarm button click
     * - Keyboard shortcuts (optional)
     */

    // Arm/Disarm buttons already have onclick in HTML
    // Could add keyboard shortcuts here
}

// ==========================================
// Periodic Updates
// ==========================================

function startPeriodicUpdates() {
    /**
     * Start periodic status updates
     *
     * TODO:
     * - Clear existing timer if any
     * - Set new interval for updates
     * - Fetch status on interval
     */

    if (updateTimer) {
        clearInterval(updateTimer);
    }

    updateTimer = setInterval(() => {
        fetchSystemStatus();
    }, CONFIG.updateInterval);
}

function stopPeriodicUpdates() {
    /**
     * Stop periodic updates (e.g., on error)
     */
    if (updateTimer) {
        clearInterval(updateTimer);
        updateTimer = null;
    }
}

// ==========================================
// API Functions
// ==========================================

async function fetchSystemStatus() {
    /**
     * Fetch current system status from API
     *
     * TODO:
     * - GET /api/status
     * - Parse response
     * - Update UI elements
     * - Handle errors
     */

    try {
        const response = await fetch('/api/status');

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        // TODO: Update UI with fetched data
        updateSystemState(data.state);
        updateSystemMetrics(data);
        updateDetectionStats(data.detections);
        updateLastUpdate();

    } catch (error) {
        console.error('Failed to fetch status:', error);
        showError('Connection error');
    }
}

async function armSystem() {
    /**
     * Arm the security system
     *
     * TODO:
     * - POST /api/arm
     * - Update UI based on response
     * - Show success/error message
     */

    try {
        // Disable button during request
        const btn = document.getElementById('btn-arm');
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Arming...';

        const response = await fetch('/api/arm', { method: 'POST' });
        const data = await response.json();

        if (data.success) {
            showSuccess('System armed successfully');
            fetchSystemStatus();  // Refresh status immediately
        } else {
            showError(data.message);
        }

    } catch (error) {
        console.error('Failed to arm system:', error);
        showError('Failed to arm system');
    } finally {
        // Re-enable button
        const btn = document.getElementById('btn-arm');
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-shield-check"></i> Arm System';
    }
}

async function disarmSystem() {
    /**
     * Disarm the security system
     *
     * TODO:
     * - POST /api/disarm
     * - Update UI based on response
     * - Show success/error message
     */

    try {
        const btn = document.getElementById('btn-disarm');
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Disarming...';

        const response = await fetch('/api/disarm', { method: 'POST' });
        const data = await response.json();

        if (data.success) {
            showSuccess('System disarmed successfully');
            fetchSystemStatus();
        } else {
            showError(data.message);
        }

    } catch (error) {
        console.error('Failed to disarm system:', error);
        showError('Failed to disarm system');
    } finally {
        const btn = document.getElementById('btn-disarm');
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-shield-slash"></i> Disarm System';
    }
}

// ==========================================
// UI Update Functions
// ==========================================

function updateSystemState(state) {
    /**
     * Update system state display
     *
     * Args:
     *   state: "armed", "disarmed", or "alarm"
     *
     * TODO:
     * - Update status badge
     * - Update state alert box
     * - Update button states
     * - Apply appropriate colors
     */

    currentState = state;

    const statusBadge = document.getElementById('system-status');
    const stateAlert = document.getElementById('system-state-alert');
    const stateText = document.getElementById('system-state-text');

    // Update badge and alert based on state
    if (state === 'armed') {
        statusBadge.className = 'badge bg-success me-3';
        statusBadge.innerHTML = '<i class="bi bi-circle-fill"></i> ARMED';

        stateAlert.className = 'alert alert-success text-center mb-0';
        stateText.innerHTML = '<i class="bi bi-shield-check"></i> ARMED';

    } else if (state === 'disarmed') {
        statusBadge.className = 'badge bg-secondary me-3';
        statusBadge.innerHTML = '<i class="bi bi-circle-fill"></i> DISARMED';

        stateAlert.className = 'alert alert-secondary text-center mb-0';
        stateText.innerHTML = '<i class="bi bi-shield-slash"></i> DISARMED';

    } else if (state === 'alarm') {
        statusBadge.className = 'badge bg-danger me-3 alarm';
        statusBadge.innerHTML = '<i class="bi bi-exclamation-triangle-fill"></i> ALARM';

        stateAlert.className = 'alert alert-danger text-center mb-0';
        stateText.innerHTML = '<i class="bi bi-exclamation-triangle-fill"></i> ALARM';
    }
}

function updateSystemMetrics(data) {
    /**
     * Update system metrics (CPU, RAM, Temperature, etc.)
     *
     * Args:
     *   data: Status object with metrics
     *
     * TODO:
     * - Update CPU usage and progress bar
     * - Update RAM usage and progress bar
     * - Update temperature and progress bar
     * - Update uptime
     * - Update camera FPS
     * - Change colors based on thresholds
     */

    // CPU Usage
    if (data.cpu_usage !== undefined) {
        const cpuValue = Math.round(data.cpu_usage);
        document.getElementById('cpu-usage').textContent = `${cpuValue}%`;

        const cpuProgress = document.getElementById('cpu-progress');
        cpuProgress.style.width = `${cpuValue}%`;

        // Change color based on usage
        cpuProgress.className = 'progress-bar';
        if (cpuValue < 70) {
            cpuProgress.classList.add('bg-success');
        } else if (cpuValue < 85) {
            cpuProgress.classList.add('bg-warning');
        } else {
            cpuProgress.classList.add('bg-danger');
        }
    }

    // RAM Usage
    if (data.ram_usage !== undefined) {
        const ramValue = Math.round(data.ram_usage);
        document.getElementById('ram-usage').textContent = `${ramValue}%`;

        const ramProgress = document.getElementById('ram-progress');
        ramProgress.style.width = `${ramValue}%`;
    }

    // Temperature
    if (data.temperature !== undefined) {
        const tempValue = Math.round(data.temperature);
        document.getElementById('temperature').textContent = `${tempValue}°C`;

        const tempProgress = document.getElementById('temp-progress');
        const tempPercent = Math.min((tempValue / 85) * 100, 100);  // 85°C = 100%
        tempProgress.style.width = `${tempPercent}%`;

        // Change color based on temperature
        tempProgress.className = 'progress-bar';
        if (tempValue < 60) {
            tempProgress.classList.add('bg-success');
        } else if (tempValue < 75) {
            tempProgress.classList.add('bg-warning');
        } else {
            tempProgress.classList.add('bg-danger');
        }
    }

    // Uptime
    if (data.uptime !== undefined) {
        document.getElementById('uptime').textContent = formatUptime(data.uptime);
    }

    // Camera FPS
    if (data.camera_fps !== undefined) {
        document.getElementById('camera-fps').textContent = `${data.camera_fps.toFixed(1)} FPS`;
    }
}

function updateDetectionStats(detections) {
    /**
     * Update detection statistics
     *
     * Args:
     *   detections: Object with total, person, animal counts
     *
     * TODO:
     * - Update total detections
     * - Update person detections
     * - Update animal detections
     * - Update last detection time
     */

    if (!detections) return;

    document.getElementById('stat-total').textContent = detections.total || 0;
    document.getElementById('stat-person').textContent = detections.person || 0;
    document.getElementById('stat-animal').textContent = detections.animal || 0;
}

function updateLastUpdate() {
    /**
     * Update "last update" timestamp
     */
    const now = new Date();
    const timeStr = now.toLocaleTimeString();
    document.getElementById('last-update').textContent = timeStr;
}

// ==========================================
// Utility Functions
// ==========================================

function updateClock() {
    /**
     * Update clock display in stream overlay
     */
    const now = new Date();
    const timeStr = now.toLocaleTimeString();
    const clockElement = document.getElementById('current-time');
    if (clockElement) {
        clockElement.textContent = timeStr;
    }
}

function formatUptime(seconds) {
    /**
     * Format uptime seconds to readable string
     *
     * Args:
     *   seconds: Uptime in seconds
     *
     * Returns:
     *   Formatted string like "2h 15m 30s"
     */
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);

    return `${hours}h ${minutes}m ${secs}s`;
}

function formatTimestamp(isoString) {
    /**
     * Format ISO timestamp to readable string
     *
     * Args:
     *   isoString: ISO 8601 timestamp
     *
     * Returns:
     *   Formatted string
     */
    const date = new Date(isoString);
    return date.toLocaleString();
}

// ==========================================
// Notification Functions
// ==========================================

function showSuccess(message) {
    /**
     * Show success notification
     *
     * TODO: Implement toast notifications or alerts
     */
    console.log('[SUCCESS]', message);
    // Could use Bootstrap Toast or simple alert
    alert(message);
}

function showError(message) {
    /**
     * Show error notification
     *
     * TODO: Implement toast notifications or alerts
     */
    console.error('[ERROR]', message);
    alert('Error: ' + message);
}

function showInfo(message) {
    /**
     * Show info notification
     *
     * TODO: Implement toast notifications
     */
    console.log('[INFO]', message);
}

// ==========================================
// Error Handling
// ==========================================

window.addEventListener('error', function(event) {
    console.error('Global error:', event.error);
});

window.addEventListener('unhandledrejection', function(event) {
    console.error('Unhandled promise rejection:', event.reason);
});

// ==========================================
// Cleanup on Page Unload
// ==========================================

window.addEventListener('beforeunload', function() {
    stopPeriodicUpdates();
});

// ==========================================
// Export for Testing (Optional)
// ==========================================

// For testing purposes, expose functions
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        armSystem,
        disarmSystem,
        fetchSystemStatus,
        updateSystemState,
        updateSystemMetrics,
        formatUptime,
    };
}
