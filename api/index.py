import os
import uuid
import string
import random
import logging
import requests
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8385486489:AAGyZGUk5Xa1yI6Qkt-b0KZhczinimJoNh4"
CHANNEL = "nagiportal"
DEVELOPER = "nagipy"

REQUIRED_CHANNELS = [
    "@nagibots",
    "@PyNagi",
    "@exelwl",
    "@dealwithwrongperson"
]

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class SimpleResetBot:
    def __init__(self, token: str):
        self.application = Application.builder().token(token).build()
        self.setup_handlers()

    def setup_handlers(self):
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help))
        self.application.add_handler(CommandHandler("reset", self.reset))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))

    async def check_subscription(self, user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
        for channel in REQUIRED_CHANNELS:
            try:
                chat_member = await context.bot.get_chat_member(channel, user_id)
                if chat_member.status in ["left", "kicked"]:
                    return False
            except Exception:
                return False
        return True

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await self.check_subscription(update.effective_user.id, context):
            await self.show_subscription_required(update, context)
            return

        await update.message.reply_text("🤖 Instagram Password Reset Bot")

    async def show_subscription_required(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [[InlineKeyboardButton(ch, url=f"https://t.me/{ch[1:]}")] for ch in REQUIRED_CHANNELS]
        await update.message.reply_text(
            "⚠️ Join all channels to use this bot",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("/reset <username or email>")

    async def reset(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text("Usage: /reset <username or email>")
            return
        await self.process_request(update, " ".join(context.args))

    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.process_request(update, update.message.text)

    async def process_request(self, update: Update, target: str):
        await update.message.reply_text(await self.send_reset_request(target))

    async def send_reset_request(self, target: str):
        try:
            data = {"username": target.lstrip("@")}
            r = requests.post(
                "https://i.instagram.com/api/v1/accounts/send_password_reset/",
                data=data,
                timeout=10
            )
            return "✅ Reset sent" if r.status_code == 200 else f"❌ Failed {r.status_code}"
        except Exception as e:
            return f"❌ Error {e}"

# 🔥 SINGLE GLOBAL INSTANCE (IMPORTANT)
bot = SimpleResetBot(TOKEN)

# 🔥 VERCEL WEBHOOK ENTRYPOINT
def handler(request):
    update = Update.de_json(request.json, bot.application.bot)
    asyncio.run(bot.application.process_update(update))
    return "ok"
    async def check_subscription(self, user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
        for channel in REQUIRED_CHANNELS:
            try:
                chat_member = await context.bot.get_chat_member(
                    chat_id=channel,
                    user_id=user_id
                )
                if chat_member.status in ['left', 'kicked']:
                    return False
            except Exception as e:
                logger.error(f"Error checking subscription to {channel}: {e}")
                return False
        return True

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        is_subscribed = await self.check_subscription(user.id, context)
        if not is_subscribed:
            await self.show_subscription_required(update, context)
            return

        text = f"""
👋 Welcome {user.first_name}!

🤖 Instagram Password Reset Bot

📌 Commands:
/reset <username>
/reset <email>
/help

🔧 Developer: @{DEVELOPER}
📢 Channel: @{CHANNEL}
"""
        keyboard = [
            [
                InlineKeyboardButton("📢 Channel", url=f"https://t.me/{CHANNEL}"),
                InlineKeyboardButton("👨‍💻 Developer", url=f"https://t.me/{DEVELOPER}")
            ]
        ]
        await update.message.reply_text(
            text,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def show_subscription_required(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = []
        for channel in REQUIRED_CHANNELS:
            channel_name = channel.replace("@", "")
            keyboard.append([InlineKeyboardButton(f"📢 Join {channel}", url=f"https://t.me/{channel_name}")])
        keyboard.append([InlineKeyboardButton("✅ Check Subscription", callback_data="check_subscription")])

        text = f"""
⚠️ Subscription Required ⚠️

You must join all channels to use this bot.
"""
        await update.message.reply_text(
            text,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        is_subscribed = await self.check_subscription(update.effective_user.id, context)
        if not is_subscribed:
            await self.show_subscription_required(update, context)
            return

        await update.message.reply_text(
            "Use /reset <username or email>",
            parse_mode='Markdown'
        )

    async def reset(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        is_subscribed = await self.check_subscription(update.effective_user.id, context)
        if not is_subscribed:
            await self.show_subscription_required(update, context)
            return

        if not context.args:
            await update.message.reply_text(
                "Usage: /reset <username or email>",
                parse_mode='Markdown'
            )
            return

        target = ' '.join(context.args).strip()
        await self.process_request(update, target)

    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        is_subscribed = await self.check_subscription(update.effective_user.id, context)
        if not is_subscribed:
            await self.show_subscription_required(update, context)
            return

        text = update.message.text.strip()
        if len(text) < 3:
            return

        await self.process_request(update, text)

    async def process_request(self, update: Update, target: str):
        chat = update.effective_chat
        await chat.send_action(action="typing")
        result = await self.send_reset_request(target)
        await update.message.reply_text(result, parse_mode='Markdown')

    async def send_reset_request(self, target: str):
        try:
            cleaned_target = target.lstrip('@')
            if "@" in cleaned_target:
                data = {"user_email": cleaned_target}
                target_type = "email"
            else:
                data = {"username": cleaned_target}
                target_type = "username"

            headers = {
                "User-Agent": "Instagram 150.0.0.0.000 Android"
            }

            response = requests.post(
                "https://i.instagram.com/api/v1/accounts/send_password_reset/",
                headers=headers,
                data=data,
                timeout=10
            )

            if response.status_code == 200:
                return f"✅ Success for {cleaned_target} ({target_type})"
            return f"❌ Failed ({response.status_code})"

        except Exception as e:
            return f"❌ Error: {str(e)[:100]}"

bot_instance = SimpleResetBot(TOKEN)

def handler(request):
    update = Update.de_json(request.json, bot_instance.application.bot)
    bot_instance.application.process_update(update)
    return "ok"
