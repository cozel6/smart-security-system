"""
Alert Manager Module - Alert Queue and Cooldown Management

This module manages alert generation, queuing, and sending.
Implements cooldown to prevent alert spam.

Responsibilities:
- Queue alerts by priority
- Implement cooldown between alerts
- Prevent duplicate alerts
- Track alert history
- Coordinate with TelegramBot for sending

Alert Priority:
- CRITICAL (3): Person detected - send immediately
- HIGH (2): Person + Animal - send with short cooldown
- LOW (1): Animal only - send with longer cooldown
- NONE (0): No detection - don't alert

Usage:
    from src.alerts.alert_manager import AlertManager
    from src.detection.yolo_detector import AlertLevel

    manager = AlertManager(telegram_bot=bot)

    # Queue alert
    manager.add_alert(
        level=AlertLevel.CRITICAL,
        message="Person detected!",
        frame=image
    )

    # Manager automatically sends based on cooldown
"""

from queue import PriorityQueue, Empty
from typing import Optional, Dict
from datetime import datetime, timedelta
import threading
import time
import numpy as np

from config.settings import settings
from src.detection.yolo_detector import AlertLevel


class Alert:
    """
    Alert data structure.

    Implements comparison for priority queue ordering.
    """

    def __init__(
        self,
        level: AlertLevel,
        message: str,
        frame: Optional[np.ndarray] = None,
        timestamp: Optional[datetime] = None,
    ):
        """
        Create alert.

        TODO:
        - Store level, message, frame
        - Set timestamp to now if not provided
        - Calculate priority (higher = more urgent)
        """
        self.level = level
        self.message = message
        self.frame = frame
        self.timestamp = timestamp or datetime.now()
        self.priority = level.value  # Higher value = higher priority

    def __lt__(self, other):
        """Compare alerts for priority queue (higher priority first)."""
        return self.priority > other.priority

    def __repr__(self) -> str:
        return f"<Alert: {self.level.name}, {self.message[:30]}...>"


class AlertManager:
    """
    Manages alert queue, cooldown, and sending.

    Processes alerts in priority order with configurable cooldown.
    """

    def __init__(
        self,
        telegram_bot=None,
        cooldown_seconds: Optional[int] = None,
    ):
        """
        Initialize alert manager.

        Args:
            telegram_bot: TelegramBot instance for sending alerts
            cooldown_seconds: Minimum seconds between alerts (default from settings)

        TODO:
        - Store telegram_bot reference
        - Load cooldown from settings
        - Initialize priority queue
        - Initialize processing thread
        - Track last alert time
        - Initialize statistics
        """
        self.telegram_bot = telegram_bot
        self.cooldown = cooldown_seconds or settings.alert_cooldown

        self.queue = PriorityQueue()
        self.processing_thread = None
        self.stop_event = threading.Event()

        self.last_alert_time = None
        self.alert_count = 0
        self.alerts_sent = 0
        self.alerts_dropped = 0

    def start(self) -> None:
        """
        Start alert processing thread.
        """
        if self.processing_thread is not None and self.processing_thread.is_alive():
            print("Alert manager already running")
            return
        
        # Clear stop event
        self.processing_thread = threading.Thread(
            target= self._process_loop,
            daemon= True
        )

        # Start thread
        self.processing_thread.start()

        print("Alert manager started")


    def add_alert(
        self,
        level: AlertLevel,
        message: str,
        frame: Optional[np.ndarray] = None,
    ) -> None:
        """
        Add alert to queue.
        """
        # Create Alert object
        alert = Alert(
            level=level,
            message=message,
            frame=frame
        )
        # Add to priority queue
        self.queue.put(alert)

        # Incremnt alert count

        self.alert_count += 1

        print(f"Alert queued: {alert.level.name} - {message[:50]}")

    def _process_loop(self) -> None:
        """
        Main processing loop (runs in thread).
        """
        while not self.stop_event.is_set():
            try:
                # Try to get alert from queue (without timeout)
                try:
                    alert = self.queue.get(timeout=1.0)
                except Empty:
                    # No alerts in queue, contiune loop
                    continue
                # Check cooldown
                if self._is_in_cooldown():
                    # In cooldown - put alert back and wait
                    wait_time = self._time_until_next_alert()

                    # Put alert back in queue 
                    self.queue.put(alert)

                    #  Wait for cooldown to expire (but check stop_event)
                    if wait_time > 0:
                        self.stop_event.wait(min(wait_time, 1.0))
                    
                    continue

                # Cooldown passed - send alert

                success = self._send_alert(alert)

                if not success:
                    # Failed to sent, increment droppped count
                    self.alerts_dropped += 1
                
                # Breif sleep between iteration
                time.sleep(0.1)
            except Exception as e:
                print(f"Error in alert processing loop: {e}")
                time.sleep(0.1)

    def _send_alert(self, alert: Alert) -> bool:
        """
        Send alert via Telegram.
        """
        try:
            # Check if telegram bot is configured
            if self.telegram_bot is None:
                print(f"Telegram bot not configured, skipping alert")
                return False
            
            # Format alert message with level emoji
            emoji_map = {
                AlertLevel.CRITICAL: "🚨",
                AlertLevel.HIGH: "⚠️",
                AlertLevel.LOW: "ℹ️",
                AlertLevel.NONE: "✓"
            }
            emoji = emoji_map.get(alert.level, "📢")
            formatted_message = f"{emoji} {alert.level.name}: {alert.message}"

            # Call telegram_bot.send_alert()
            success = self.telegram_bot.send_alert(
                message=formatted_message,
                image=alert.frame
            )
            if success:
                # Update last alert time
                self.last_alert_time = datetime.now()

                # Increment alert sent
                self.alerts_sent += 1

                print(f"Alert sent successfully: {alert.level.name}")

                return True
            else:
                print(f"Failed to send alert: {alert.level.name}")
                return False
            
        except Exception as e:
            print(f"Error sending alert: {e}")
            return False
                

    def _is_in_cooldown(self) -> bool:
        """
        Check if in cooldown period.
        """
        # If no previous alert, not in cooldown
        if self.last_alert_time is None:
            return False
        
        # Calculate time since last alert
        time_since_last = (datetime.now() - self.last_alert_time).total_seconds()

        # Retrun true if less that cooldown seconds
        return time_since_last < self.cooldown
    

    def _time_until_next_alert(self) -> float:
        """
        Calculate seconds until next alert can be sent.
        """
        # If no previous alert, can sent now
        if self.last_alert_time is None:
            return 0.0
        
        # Calulate time since last alert
        time_since_last = (datetime.now() - self.last_alert_time).total_seconds()

        # Calulate remaining cooldown time
        remaining = self.cooldown - time_since_last

        # Rest 0 if cooldown expired
        return max(0.0, remaining)


    def clear_queue(self) -> int:
        """
        Clear all queued alerts.
        """
        # Count alerts in queue
        count = self.queue.qszie()

        # Clear queue by creating new PriorityQueue
        self.queue = PriorityQueue()

        print(f"Cleared {count} alerts. form queue")

        return count

    def get_queue_size(self) -> int:
        """
        Get number of queued alerts.
        """
        return self.queue.qsize()

    def set_cooldown(self, seconds: int) -> None:
        """
        Update cooldown period.

        Args:
            seconds: New cooldown in seconds

        TODO:
        - Validate seconds is positive
        - Update self.cooldown
        """
        self.cooldown = seconds

    def get_statistics(self) -> Dict:
        """
        Get alert statistics.
        """
        # Calulate send rate
        send_rate = (
            self.alerts_sent / self.alert_count * 100
            if self.alert_count > 0
            else 0.0
        )

        return {
            'alert_count': self.alert_count,
            'alerts_sent': self.alerts_sent,
            'alerts_dropped': self.alerts_dropped,
            'queue_size': self.queue.qsize(),
            'send_rate': round(send_rate, 2)
        }   


    def stop(self) -> None:
        """
        Stop alert manager.
        """
        print("Stopping alert manager...")
    
        # Set stop event
        self.stop_event.set()
        
        # Wait for processing thread to finish
        if self.processing_thread is not None and self.processing_thread.is_alive():
            self.processing_thread.join(timeout=5.0)
        
        # Clear queue
        cleared = self.clear_queue()
        
        # Log statistics
        stats = self.get_statistics()
        print(f"Alert manager stopped:")
        print(f"  Total alerts: {stats['alert_count']}")
        print(f"  Alerts sent: {stats['alerts_sent']}")
        print(f"  Alerts dropped: {stats['alerts_dropped']}")
        print(f"  Cleared from queue: {cleared}")

    def __repr__(self) -> str:
        """String representation."""
        return f"<AlertManager: queue={self.get_queue_size()}, sent={self.alerts_sent}>"


if __name__ == "__main__":
    """Test alert manager."""
    print("Alert Manager test - TODO: Implement test code")
    pass
