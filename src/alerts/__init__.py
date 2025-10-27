"""
Alerts Package

This package contains alert and notification modules:
- TelegramBot: Telegram bot interface for remote control and alerts
- AlertManager: Alert queue management and cooldown handling
"""

from .telegram_bot import TelegramBot
from .alert_manager import AlertManager

__all__ = ['TelegramBot', 'AlertManager']
