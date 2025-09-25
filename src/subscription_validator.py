import os
from telethon import TelegramClient, Button
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.errors import UserNotParticipantError
from yaml import safe_load


class SubscriptionValidator:
    def __init__(self, bot: TelegramClient, config_path: str = './config.yaml'):
        self.bot = bot
        self.required_channel = None
        
        # Load from environment variable first, then config file
        self.required_channel = os.getenv('REQUIRED_CHANNEL')
        
        if not self.required_channel:
            try:
                with open(config_path) as f:
                    config = safe_load(f)
                    self.required_channel = config.get('required_channel')
            except FileNotFoundError:
                pass
    
    def _channel_link(self, name: str) -> str:
        """Convert channel name to clickable link"""
        n = name.strip()
        if n.startswith('@'):
            n = n[1:]
        return f'https://t.me/{n}'
    
    async def is_subscribed(self, user_id: int) -> bool:
        """Check if user is subscribed to the required channel"""
        if not self.required_channel:
            return True
        
        try:
            await self.bot(GetParticipantRequest(self.required_channel, user_id))
            return True
        except UserNotParticipantError:
            return False
        except Exception:
            # Be conservative: if unsure, deny access
            return False
    
    async def ensure_subscription(self, event) -> bool:
        """Ensure user is subscribed, show message if not"""
        if not self.required_channel:
            return True
        
        sender = await event.get_sender()
        is_sub = await self.is_subscribed(sender.id)
        
        if not is_sub:
            url = self._channel_link(self.required_channel)
            try:
                await self.bot.send_message(
                    sender,
                    message="Подпишитесь на канал, чтобы продолжить.",
                    buttons=[Button.url('Подписаться', url)]
                )
            except Exception:
                pass
        
        return is_sub
    
    async def answer_callback_with_subscription_check(self, event) -> bool:
        """Answer callback query with subscription check, return True if subscribed"""
        if not self.required_channel:
            return True
        
        sender = await event.get_sender()
        is_sub = await self.is_subscribed(sender.id)
        
        if not is_sub:
            try:
                await event.answer("Подпишитесь на канал, чтобы продолжить.", alert=True)
            except Exception:
                pass
        
        return is_sub
