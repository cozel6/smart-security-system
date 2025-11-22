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
        def generate():
            """Generator function for video streaming."""
            while True:
                # Get frame from callback
                if self.get_frame_callback:
                    frame = self.get_frame_callback()
                    
                    if frame is not None:
                        # Encode frame as JPEG
                        import cv2
                        ret, buffer = cv2.imencode('.jpg', frame)
                        
                        if ret:
                            frame_bytes = buffer.tobytes()
                            
                            # Yield frame in multipart format
                            yield (b'--frame\r\n'
                                b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                
                # Small delay to control frame rate
                import time
                time.sleep(0.033)  # ~30 FPS

        # Return streaming response
        return Response(
            generate(),
            mimetype='multipart/x-mixed-replace; boundary=frame'
        )

    def api_status(self):
        """
        Get system status (API endpoint).
        """
        # Call callback if available
        if self.get_status_callback:
            status = self.get_status_callback()
            return jsonify(status)
        else:
        #Return dummy status if no callbacks,
            return jsonify(
                {
                    "armed": False,
                    "uptime" : "0:00:00",
                    "camera_fps" : 0,
                    "cpu_usage" : "0%",
                    "memory_usage": "0%",
                    "last_detection": None
                }
            )

    def api_arm(self):
        """
        Arm system (API endpoint).
        """
        # Call calback if available
        if self.arm_callback:
            try:
                self.arm_callback()
                return jsonify({
                    "success" : True,
                    "message": "System armed successfully"
                })
            except Exception as e:
                return jsonify({
                    "success": False,
                    "message": f"Failed to arm system: {str(e)}"
                }), 500
        else:
            return jsonify({
                "success": False,
                "message": "Arm callback not registered"
            }), 400
        
    def api_disarm(self):
        """
        Disarm system (API endpoint).
        """
        # Call callback if available
        if self.disarm_callback:
            try:
                self.disarm_callback()
                return jsonify({
                    "success": True,
                    "message": "System disarmed successfully"
                })
            except Exception as e:
                return jsonify({
                    "success": False,
                    "message": f"Failed to disarm system: {str(e)}"
                }), 500
        else:
            return jsonify({
                "success": False,
                "message": "Disarm callback not registered"
            }), 400

    def api_snapshot(self):
        """
        Get current camera frame (API endpoint).
        """
        # Get current frame
        if self.get_frame_callback:
            frame = self.get_frame_callback()
            
            if frame is not None:
                import cv2
                # Encode as JPEG
                ret, buffer = cv2.imencode('.jpg', frame)
                
                if ret:
                    return Response(buffer.tobytes(), mimetype='image/jpeg')
            
        return jsonify({"error": "No frame available"}), 404
        

    def api_logs(self):
        """
        Get recent event logs (API endpoint).

        TODO:
        - Read recent log entries (last 20)
        - Parse and format as JSON array
        - Return with pagination support
        """
        # TODO: Implement logs API
        return jsonify({
            "logs": [],
            "count": 0
        }) # For now, return empty logs

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
        if self.running:
            print(f"Server already running at {self.get_url()}")
            return
        
        # Create server thread
        self.server_thread = threading.Thread(target=self._run_server, daemon=True)
        self.running = True

        # Start server
        self.server_thread.start()

        print(f"Server started at {self.get_url()}")


    def _run_server(self) -> None:
        """
        Run Flask server (called in thread).
        """
        try:
            self.app.run(
                host = self.host,
                port = self.port,
                debug=self.debug,
                use_reloader = False, # for not create dublicate threads
                threaded = True
            )
        except Exception as e:
            print(f"Server error: {e}")
            self.running = False

    def stop(self) -> None:
        """
        Stop Flask server.

        TODO:
        - Set running flag to False
        - Shutdown Flask server gracefully
        - Wait for thread to finish
        - Log shutdown
        """
        if not self.running:
            print("Server not running")
            return
        print("Stopping Flask server...")
        self.running = False

        # Note: Flask doesn't have a clean shutdown method in threading mode
        # The daemon thread will stop when main program exits
        print("✓ Flask server stopped")

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
    print("=== Testing Flask Server ===\n")

    # Create server instance
    server = FlaskServer(host="127.0.0.1", port=5001)
    print(f"✓ Server created: {server}")

    # Test start
    server.start()
    print(f"✓ Server running: {server.is_running()}")
    print(f"✓ URL: {server.get_url()}")

    print("\n→ Open browser at http://127.0.0.1:5001")
    print("→ Press Ctrl+C to stop\n")

    # Keep server running
    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nStopping server...")
        server.stop()
        print("✓ Test completed")
