"""
Flask Server Module - Web Dashboard and API

This module provides web interface for system monitoring and control.

Features:
- Live MJPEG video streaming
- System status dashboard
- Arm/Disarm controls
- Event logs viewer
- API endpoints for remote control

Endpoints:
- GET  / - Dashboard home page
- GET  /video_feed - MJPEG stream
- POST /api/arm - Arm system
- POST /api/disarm - Disarm system
- GET  /api/status - System status JSON
- GET  /api/snapshot - Current frame
- GET  /api/logs - Recent events

Usage:
    from src.streaming.flask_server import FlaskServer

    server = FlaskServer()
    server.start()  # Runs in background thread

    # Access at http://[raspberry_pi_ip]:5000
"""

from flask import Flask, render_template, Response, jsonify, request
from flask_cors import CORS
import threading
from typing import Optional, Callable, Generator
import json
from datetime import datetime

from config.settings import settings


class FlaskServer:
    """
    Flask web server for dashboard and API.

    Runs in separate thread to avoid blocking main application.
    """

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        debug: bool = False,
    ):
        """
        Initialize Flask server.

        Args:
            host: Server host (default from settings)
            port: Server port (default from settings)
            debug: Debug mode (default False)

        TODO:
        - Load host and port from settings
        - Initialize Flask app
        - Configure CORS for API access
        - Register routes
        - Initialize callback storage for system control
        - Initialize server thread
        """
        self.host = host or settings.flask_host
        self.port = port or settings.flask_port
        self.debug = debug

        self.app = Flask(__name__, template_folder='../../web/templates', static_folder='../../web/static')
        CORS(self.app)

        # Callbacks (will be set by SystemManager)
        self.get_frame_callback = None
        self.get_status_callback = None
        self.arm_callback = None
        self.disarm_callback = None

        # Server thread
        self.server_thread = None
        self.running = False

        # Register routes
        self._register_routes()

    def _register_routes(self) -> None:
        """
        Register Flask routes.

        TODO:
        - Register all routes with appropriate methods
        - Dashboard routes (GET)
        - API routes (GET/POST)
        - Error handlers (404, 500)
        """
        # Dashboard routes
        self.app.route('/')(self.index)
        self.app.route('/video_feed')(self.video_feed)

        # API routes
        self.app.route('/api/status', methods=['GET'])(self.api_status)
        self.app.route('/api/arm', methods=['POST'])(self.api_arm)
        self.app.route('/api/disarm', methods=['POST'])(self.api_disarm)
        self.app.route('/api/snapshot', methods=['GET'])(self.api_snapshot)
        self.app.route('/api/logs', methods=['GET'])(self.api_logs)

    def index(self):
        """
        Render dashboard home page.

        TODO:
        - Return render_template('index.html')
        - Pass any necessary context variables
        """
        return render_template('index.html')

    def video_feed(self):
        """
        MJPEG video stream endpoint.

        TODO:
        - Return Response with MJPEG stream
        - Use VideoStreamer to generate frames
        - Set appropriate mimetype: multipart/x-mixed-replace
        """
        # TODO: Implement video streaming
        pass

    def api_status(self):
        """
        Get system status (API endpoint).

        TODO:
        - Call get_status_callback to get current status
        - Return JSON with:
            - armed: bool
            - uptime: seconds
            - last_detection: timestamp
            - cpu_usage: percentage
            - ram_usage: percentage
            - temperature: celsius (Raspberry Pi)
        """
        # TODO: Implement status API
        pass

    def api_arm(self):
        """
        Arm system (API endpoint).

        TODO:
        - Check if arm_callback is set
        - Call arm_callback()
        - Return JSON response:
            - success: bool
            - message: string
        """
        # TODO: Implement arm API
        pass

    def api_disarm(self):
        """
        Disarm system (API endpoint).

        TODO:
        - Check if disarm_callback is set
        - Call disarm_callback()
        - Return JSON response
        """
        # TODO: Implement disarm API
        pass

    def api_snapshot(self):
        """
        Get current camera frame (API endpoint).

        TODO:
        - Call get_frame_callback to get latest frame
        - Convert to JPEG
        - Return as image response
        """
        # TODO: Implement snapshot API
        pass

    def api_logs(self):
        """
        Get recent event logs (API endpoint).

        TODO:
        - Read recent log entries (last 20)
        - Parse and format as JSON array
        - Return with pagination support
        """
        # TODO: Implement logs API
        pass

    def register_callbacks(
        self,
        get_frame: Optional[Callable] = None,
        get_status: Optional[Callable] = None,
        arm: Optional[Callable] = None,
        disarm: Optional[Callable] = None,
    ) -> None:
        """
        Register callback functions for system interaction.

        TODO:
        - Store callback functions
        - Will be called by route handlers
        """
        self.get_frame_callback = get_frame
        self.get_status_callback = get_status
        self.arm_callback = arm
        self.disarm_callback = disarm

    def start(self) -> None:
        """
        Start Flask server in background thread.

        TODO:
        - Create server thread
        - Set daemon=True
        - Start thread
        - Set running flag
        - Log server URL
        """
        # TODO: Implement server startup
        pass

    def _run_server(self) -> None:
        """
        Run Flask server (called in thread).

        TODO:
        - Call app.run() with:
            - host=self.host
            - port=self.port
            - debug=self.debug
            - use_reloader=False (important for threading)
        """
        # TODO: Implement server run
        pass

    def stop(self) -> None:
        """
        Stop Flask server.

        TODO:
        - Set running flag to False
        - Shutdown Flask server gracefully
        - Wait for thread to finish
        - Log shutdown
        """
        # TODO: Implement server shutdown
        pass

    def is_running(self) -> bool:
        """Check if server is running."""
        return self.running

    def get_url(self) -> str:
        """Get server URL."""
        return f"http://{self.host}:{self.port}"

    def __repr__(self) -> str:
        """String representation."""
        status = "running" if self.running else "stopped"
        return f"<FlaskServer: {self.get_url()}, {status}>"


if __name__ == "__main__":
    """Test Flask server."""
    print("Flask Server test - TODO: Implement test code")
    pass
