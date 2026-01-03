"""
Telegram Bot Module - Remote Control and Alerts

This module provides Telegram bot interface for:
- System control (arm/disarm)
- Real-time alerts with photos
- Status queries
- Remote snapshots
- Event logs

Supported Commands:
- /start - Initialize bot
- /help - Show command list
- /arm - Arm the security system
- /disarm - Disarm the system
- /status - Get system status
- /snapshot - Get current camera frame
- /logs - View recent events

Usage:
    from src.alerts.telegram_bot import TelegramBot

    bot = TelegramBot()
    bot.start()

    # Send alert
    bot.send_alert("CRITICAL: Person detected!", frame=image, alert_type="person")

    # Bot runs until stopped
    bot.stop()
"""

from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes
import io
from PIL import Image
import numpy as np
from typing import Optional, Callable
from datetime import datetime

from config.settings import settings


class TelegramBot:
    """
    Telegram bot for remote control and notifications.

    Handles commands from authorized users and sends alerts with images.
    """

    def __init__(self, token: Optional[str] = None, chat_id: Optional[str] = None):
        """
        Initialize Telegram bot.

        Args:
            token: Bot token from BotFather (default from settings)
            chat_id: Authorized chat ID (default from settings)

        TODO:
        - Load token and chat_id from settings if not provided
        - Initialize bot application
        - Register command handlers
        - Initialize callback storage for system control
        """
        self.token = token or settings.telegram_bot_token
        self.chat_id = chat_id or settings.telegram_chat_id

        self.application = None
        self.bot = None

        # Callbacks for system control (will be set by SystemManager)
        self.on_arm_callback = None
        self.on_disarm_callback = None
        self.get_status_callback = None
        self.get_snapshot_callback = None

    def start(self) -> None:
        """
        Start Telegram bot with polling.
        """
        import asyncio

        # Create event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Create Application
        self.application = Application.builder().token(self.token).build()
        self.bot = self.application.bot

        # Register command handlers
        self.application.add_handler(CommandHandler("start", self.cmd_start))
        self.application.add_handler(CommandHandler("help", self.cmd_help))
        self.application.add_handler(CommandHandler("arm", self.cmd_arm))
        self.application.add_handler(CommandHandler("disarm", self.cmd_disarm))
        self.application.add_handler(CommandHandler("status", self.cmd_status))
        self.application.add_handler(CommandHandler("snapshot", self.cmd_snapshot))
        self.application.add_handler(CommandHandler("logs", self.cmd_logs))
        self.application.add_handler(CommandHandler("server", self.cmd_server))


        print(f"Telegram bot started. Chat ID: {self.chat_id}")

        # Initialize and run the application manually in this thread
        # This avoids signal handler issues when running in non-main thread
        loop.run_until_complete(self.application.initialize())
        loop.run_until_complete(self.application.start())

        # Start polling for updates
        loop.run_until_complete(self.application.updater.start_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES
        ))

        # Keep running forever (until stop is called)
        loop.run_forever()

    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle /start command.
        """
        chat_id = update.effective_chat.id

        if not self._is_authorized(chat_id):
            await update.message.reply_text(
                f"⛔ Unauthorized access denied.\n"
                f"Your chat ID: {chat_id}"
            )
            return
        
        await update.message.reply_text(
            "🔐 *Smart Security System*\n\n"
            "Welcome! Bot is ready.\n\n"
            "Use /help to see available commands.",
            parse_mode="Markdown"
        )

    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle /help command.
        """
        help_text = (
            "🔐 *Smart Security System - Commands*\n\n"
            "🎮 *Control:*\n"
            "/arm - Arm the security system\n"
            "/disarm - Disarm the system\n"
            "/status - Get system status\n\n"
            "📸 *Media:*\n"
            "/snapshot - Get current camera frame\n\n"
            "📋 *Information:*\n"
            "/logs - View recent events\n"
            "/help - Show this help message\n"
            "/server - View live dashboard URL\n"
        )

        await update.message.reply_text(help_text, parse_mode="Markdown")

    async def cmd_arm(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle /arm command.
        """
        chat_id = update.effective_chat.id

        if not self._is_authorized(chat_id):
            await update.message.reply_text("⛔ Unauthorized access denied.")
            return
        
        # Call the callback if set
        if self.on_arm_callback:
            try:
                self.on_arm_callback()
                await update.message.reply_text(
                    "✅ *System ARMED*\n\n"
                    "Security system is now acctive.\n"
                    "You will receive alerts for any detections.",
                    parse_mode="Markdown"
                )
            except Exception as e:
                await update.message.reply_text(
                    f"❌ Error arming system: {e}"
                )
        else:
            await update.message.reply_text(
            "✅ *ARM command received*\n\n"
            "(System callback not connected yet)",
            parse_mode="Markdown"
        )

    async def cmd_disarm(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle /disarm command.
        """
        chat_id = update.effective_chat.id

        if not self._is_authorized(chat_id):
            await update.message.reply_text("⛔ Unauthorized access denied.")
            return

        # Call the callback if set
        if self.on_disarm_callback:
            try:
                self.on_disarm_callback()
                await update.message.reply_text(
                    "🔓 *System DISARMED*\n\n"
                    "Security system is now inactive.\n"
                    "No alerts will be sent.",
                    parse_mode="Markdown"
                )
            except Exception as e:
                await update.message.reply_text(
                    f"❌ Error disarming system: {e}"
                )
        else:
            await update.message.reply_text(
                "🔓 *DISARM command received*\n\n"
                "(System callback not connected yet)",
                parse_mode="Markdown"
            )

    async def cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle /status command.
        """
        chat_id = update.effective_chat.id
    
        if not self._is_authorized(chat_id):
            await update.message.reply_text("⛔ Unauthorized access denied.")
            return
        
        # Get status from callback if set
        if self.get_status_callback:
            try:
                status_data = self.get_status_callback()
                
                # Format status message
                status_msg = (
                    f"📊 *System Status*\n\n"
                    f"🔒 State: {status_data.get('state', 'Unknown')}\n"
                    f"⏱ Uptime: {status_data.get('uptime', 'N/A')}\n"
                    f"💻 CPU: {status_data.get('cpu', 'N/A')}%\n"
                    f"🧠 RAM: {status_data.get('ram', 'N/A')}%\n"
                    f"🌡 Temp: {status_data.get('temp', 'N/A')}°C\n"
                    f"📸 Camera: {status_data.get('camera', 'Unknown')}\n"
                    f"🔍 Detections: {status_data.get('detections', 0)}\n"
                    f"👤 Last detection: {status_data.get('last_detection', 'None')}"
                )
                
                await update.message.reply_text(status_msg, parse_mode="Markdown")
            except Exception as e:
                await update.message.reply_text(
                    f"❌ Error getting status: {e}"
                )
        else:
            # Default status when callback not set
            import psutil
            from datetime import datetime
            
            cpu_percent = psutil.cpu_percent(interval=1)
            ram_percent = psutil.virtual_memory().percent
            
            status_msg = (
                f"📊 *System Status*\n\n"
                f"🔒 State: Not connected\n"
                f"💻 CPU: {cpu_percent}%\n"
                f"🧠 RAM: {ram_percent}%\n"
                f"📸 Camera: Unknown\n\n"
                f"(System callback not connected yet)"
            )
            
            await update.message.reply_text(status_msg, parse_mode="Markdown")

    async def cmd_snapshot(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle /snapshot command.
        """
        # Get chat id and check authorization
        chat_id = update.effective_chat.id

        if not self._is_authorized(chat_id):
            await update.message.reply_text("⛔ Unauthorized access denied.")
            return
        
        try:
            # Check if callback exists
            if not self.get_snapshot_callback:
                await update.message.reply_text("❌ Camera not available")
                return
            
            # Get frame from camera
            frame = self.get_snapshot_callback()
            if frame is None:
                await update.message.reply_text("❌ Failed to capture snapshot")
                return

             # Convert frame using helper
            from src.utils.helpers import frame_to_pil
            pil_image = frame_to_pil(frame)

            # Convert to BytesIO
            bio = io.BytesIO()
            pil_image.save(bio, format='JPEG', quality=85)
            bio.seek(0)

            # Create caption with timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            caption = f"📸 Snapshot\n🕒 {timestamp}"

            # Send photo (AWAIT - we're in async context)
            await update.message.reply_photo(photo=bio, caption=caption)      

        except Exception as e:
            await update.message.reply_text(
                f"❌ Error getting snapshot: {e}"
            )

    async def cmd_logs(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle /logs command.
        """
        chat_id = update.effective_chat.id

        if not self._is_authorized(chat_id):
            await update.message.reply_text("⛔ Unauthorized access denied.")
            return

        try:
            from config.settings import settings
            from collections import deque
            from pathlib import Path

            # Get log file path from settings
            log_path = Path(settings.log_file)

            if not log_path.exists():
                await update.message.reply_text("📋 No logs available yet")
                return

            # Read last 15 lines (memory efficient with deque)
            try:
                with open(log_path, 'r', encoding='utf-8') as f:
                    lines = list(deque(f, maxlen=15))
            except Exception as e:
                await update.message.reply_text(f"❌ Error reading logs: {e}")
                return

            # Format message
            if not lines:
                message = "📋 Log file is empty"
            else:
                header = "📋 *Recent Logs (last 15 lines)*\n\n"
                log_content = "".join(lines)
                message = header + f"```\n{log_content}\n```"

            # Handle Telegram 4096 char limit
            MAX_LENGTH = 4096
            if len(message) > MAX_LENGTH:
                # Reduce lines gradually
                while len(message) > MAX_LENGTH and len(lines) > 5:
                    lines = lines[1:]  # Remove oldest line
                    log_content = "".join(lines)
                    message = header + f"```\n{log_content}\n```"

                # Final truncation if still too long
                if len(message) > MAX_LENGTH:
                    truncate_msg = "\n```\n... (truncated)"
                    message = message[:MAX_LENGTH - len(truncate_msg)] + truncate_msg

            # Send with Markdown formatting
            await update.message.reply_text(message, parse_mode="Markdown")

        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")


    def send_alert(
        self,
        message: str,
        frame: Optional[np.ndarray] = None,
        alert_type: str = "info"
   ) -> None:
        """
        Send alert message with optional image.
        """
        try:
            # Map alert type to emoji
            emoji_map = {
                'info': 'ℹ️',
                'warning': '⚠️',
                'critical': '🚨',
                'person': '👤',
                'animal': '🐾'
            }
            emoji = emoji_map.get(alert_type, 'ℹ️')

            # Add timestamp
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Format message with emoji and timestamp
            formatted_message = f"{emoji} {message}\n\n🕒 {timestamp}"

             # Send based on frame availability
            if frame is not None:
                try:
                    self.send_photo(frame, caption=formatted_message)
                except Exception as e:
                    print(f"Photo send failed, fallback to text: {e}")
                    self.send_message(formatted_message)
            else:
                self.send_message(formatted_message)

        except Exception as e:
            print(f"Error sending alert: {e}")

    def send_message(self, text: str) -> None:
        """
        Send plain text message.
        """
        try:
            import asyncio
            asyncio.run(self.bot.send_message(chat_id=self.chat_id, text=text))
        except Exception as e:
            print(f"Error sending message: {e}")

    def send_photo(self, frame: np.ndarray, caption: str = "") -> None:
        """
        Send photo with optional caption.
        """
        try:
            # Validate frame
            if frame is None or not isinstance(frame, np.ndarray):
                raise ValueError("Invalid frame")

            # Use existing helper for BGR→RGB→PIL conversion
            from src.utils.helpers import frame_to_pil
            pil_image = frame_to_pil(frame)

            # Convert to BytesIO for upload
            bio = io.BytesIO()
            pil_image.save(bio, format='JPEG', quality=85)
            bio.seek(0)  # CRITICAL: reset position

            # Send using asyncio.run (same pattern as send_message)
            import asyncio
            asyncio.run(
                self.bot.send_photo(
                    chat_id=self.chat_id,
                    photo=bio,
                    caption=caption or None
                )
            )

        except Exception as e:
            print(f"Error sending photo: {e}")

    def _is_authorized(self, chat_id: int) -> bool:
        """
        Check if user is authorized.
        """
        return str(chat_id) == str(self.chat_id)

    def register_callbacks(
        self,
        on_arm: Optional[Callable] = None,
        on_disarm: Optional[Callable] = None,
        get_status: Optional[Callable] = None,
        get_snapshot: Optional[Callable] = None,
    ) -> None:
        """
        Register callback functions for system control.
        """
        self.on_arm_callback = on_arm
        self.on_disarm_callback = on_disarm
        self.get_status_callback = get_status
        self.get_snapshot_callback = get_snapshot

    async def cmd_server(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
            Handle /server command.
        """
        chat_id = update.effective_chat.id

        if not self._is_authorized(chat_id):
            await update.message.reply_text("⛔ Unauthorized access denied.")
            return

        try:
            from config.settings import settings
            import socket
            
            # Get server port
            port = settings.flask_port if hasattr(settings, 'flask_port') else 5001
            
            # Get local IP address
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
                s.close()
            except:
                local_ip = "192.168.x.x"
            
            # Build URLs
            local_url = f"http://127.0.0.1:{port}"
            network_url = f"http://{local_ip}:{port}"
            
            # Format message WITHOUT Markdown for URLs
            message = (
                "🖥️ *Smart Security Dashboard*\n\n"
                f"🌐 Local Access:\n"
                f"{local_url}\n\n"  # Plain URL, no Markdown syntax
                f"📡 Network Access:\n"
                f"{network_url}\n\n"
                f"📊 View live camera feed, detections, and system stats!"
            )

            await update.message.reply_text(
                message, 
                parse_mode="Markdown",
                disable_web_page_preview=False
            )


        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")


    def stop(self) -> None:
        """
        Stop Telegram bot.
        """
        if self.application:
            print("Stopping Telegram bot...")
            import asyncio

            # Get the event loop for this thread
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Stop the updater and application
                    loop.run_until_complete(self.application.updater.stop())
                    loop.run_until_complete(self.application.stop())
                    loop.run_until_complete(self.application.shutdown())
                    # Stop the event loop
                    loop.stop()
            except Exception as e:
                print(f"Error stopping bot: {e}")

            print("Telegram bot stopped.")

    def __repr__(self) -> str:
        """String representation."""
        return f"<TelegramBot: chat_id={self.chat_id}>"


if __name__ == "__main__":
    """Test Telegram bot."""
    print("Telegram Bot test - TODO: Implement test code")
    pass
