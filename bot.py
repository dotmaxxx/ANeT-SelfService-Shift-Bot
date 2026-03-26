import asyncio, os
from anet import Driver
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.constants import ParseMode

authorized = [6823894454]  # Replace this with your Telegram user ID


class Bot:
    def __init__(self, token, driver: Driver):
        self.driver = driver
        self.token = token
        self.shiftCount = -1
        self.doAutoScan = False
        self.interval = 540  # 15 minutes default
        self.timeout = 15
        self.scans_done = 0

        # Chat targets (replace with your actual chat IDs)
        self.chat_id = int(os.getenv("CHAT_ID", "0"))
        self.mfa_chat_id = int(os.getenv("MFA_ID", "0"))
        self.priority_id = int(os.getenv("PRIORITY_ID", "0"))

        self.app = ApplicationBuilder().token(token).build()

        # Register commands
        self.app.add_handler(CommandHandler("scan", self.cmd_scan))
        self.app.add_handler(CommandHandler("startscan", self.cmd_start))
        self.app.add_handler(CommandHandler("stopscan", self.cmd_stop))
        self.app.add_handler(CommandHandler("interval", self.cmd_interval))
        self.app.add_handler(CommandHandler("mfa", self.cmd_mfa))
        self.app.add_handler(CommandHandler("debug", self.cmd_debug))
        self.app.add_handler(CommandHandler("id", self.cmd_id))
        self.app.add_handler(CommandHandler("scaninfo", self.cmd_scaninfo))
        self.app.add_handler(CommandHandler("timeout", self.cmd_timeout))
        self.app.add_handler(CommandHandler("patchnotes", self.cmd_patchnotes))
        self.app.add_handler(CommandHandler("publish", self.cmd_publish))

    async def run(self):
        print("Starting Telegram bot...")
        asyncio.create_task(self.autoScan())
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling()
        print("Bot Online")

        logged_in = await self.driver.isLoggedIn()
        if not logged_in:
            #await self.log("Not logged in — attempting login...")
            await self.driver.login()
            #await self.log("Login complete.")
        else:
            await self.log("Already logged in.")

        await asyncio.Event().wait()

    # ===================
    # Utility Senders
    # ===================
    async def log(self, text):
        """Send to log channel or console"""
        if self.chat_id:
            await self.app.bot.send_message(self.chat_id, text)
        else:
            print(f"[LOG] {text}")

    async def message_all(self, text):
        """Send to main announcement channel"""
        if self.chat_id:
            await self.app.bot.send_message(self.chat_id, text, parse_mode=ParseMode.MARKDOWN)
        else:
            print(f"[MSG] {text}")

    async def message_priority(self, text):
        """Send to main announcement channel"""
        if self.chat_id:
            await self.app.bot.send_message(self.priority_id, text, parse_mode=ParseMode.MARKDOWN)
        else:
            print(f"[MSG] {text}")

    async def mfa_alert(self, text):
        """Send MFA alerts"""
        if self.mfa_chat_id:
            await self.app.bot.send_message(self.mfa_chat_id, text, parse_mode=ParseMode.MARKDOWN)
        else:
            print(f"[MFA] {text}")

    # ===================
    # Core Functions
    # ===================
    async def checkShifts(self, auto: bool = False):
        newShiftCount = await self.driver.getShifts()
        if newShiftCount > self.shiftCount:
            await self.message_priority(f"🚨 *New Shifts Detected!* (Count: {newShiftCount})\nTo alert the main group use /publish!")
        elif not auto:
            await self.log(f"No new shifts (Count: {newShiftCount})")
        self.shiftCount = newShiftCount

    async def autoScan(self):
        start = None
        while True:
            if self.doAutoScan:
                if start is None:
                    start = asyncio.get_event_loop().time()

                elapsed = asyncio.get_event_loop().time() - start
                if elapsed < self.interval:
                    await asyncio.sleep(0.5)
                else:
                    start = None
                    # await self.log("Scanning now...")
                    self.scans_done += 1
                    await self.checkShifts(auto=True)
            else:
                await asyncio.sleep(5)

    # ===================
    # Commands
    # ===================
    async def cmd_scan(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id not in authorized:
            await update.message.reply_text(f"Not authorized to use this command. (Originally from: {update.effective_user.full_name}\nID: {update.effective_user.id})")
            return
        self.message_chat_id = update.effective_chat.id
        self.log_chat_id = update.effective_chat.id
        await update.message.reply_text("Running scan... please wait (up to 60s)")
        await self.checkShifts()

    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id not in authorized:
            await update.message.reply_text(f"Not authorized to use this command. (Originally from: {update.effective_user.full_name}\nID: {update.effective_user.id})")
            return
        if self.doAutoScan:
            await update.message.reply_text("Auto-Scanning already enabled!")
        else:
            self.scans_done = 0
            self.doAutoScan = True
            self.message_chat_id = update.effective_chat.id
            self.log_chat_id = update.effective_chat.id
            await update.message.reply_text("✅ Auto-Scanning ON")

    async def cmd_stop(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id not in authorized:
            await update.message.reply_text(f"Not authorized to use this command. (Originally from: {update.effective_user.full_name}\nID: {update.effective_user.id})")
            return
        if not self.doAutoScan:
            await update.message.reply_text("Auto-Scanning already disabled!")
        else:
            self.doAutoScan = False
            await update.message.reply_text("⛔ Auto-Scanning OFF")

    async def cmd_debug(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id not in authorized:
            await update.message.reply_text(f"Not authorized to use this command. (Originally from: {update.effective_user.full_name}\nID: {update.effective_user.id})")
            return
        await update.message.reply_text("TODO (Debug info here)")

    async def cmd_interval(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id not in authorized:
            await update.message.reply_text(f"Not authorized to use this command. (Originally from: {update.effective_user.full_name}\nID: {update.effective_user.id})")
            return
        if len(context.args) != 1:
            await update.message.reply_text("Usage: /interval <seconds>")
            return
        old = self.interval
        self.interval = float(context.args[0])
        await update.message.reply_text(f"⏱ Interval changed: {old}s → {self.interval}s")

    async def cmd_mfa(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id not in authorized:
            await update.message.reply_text(f"Not authorized to use this command. (Originally from: {update.effective_user.full_name}\nID: {update.effective_user.id})")
            return
        if len(context.args) != 1:
            await update.message.reply_text("Usage: /mfa <code>")
            return
        code = context.args[0]
        self.driver.pending_code = code
        self.mfa_chat_id = update.effective_chat.id
        await update.message.reply_text(f"MFA code `{code}` received and sent to login process.")

    async def cmd_id(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Helper command to get chat ID"""
        await update.message.reply_text(f"Chat ID: `{update.effective_chat.id}`", parse_mode=ParseMode.MARKDOWN)

    async def cmd_scaninfo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(f"Scans done: {self.scans_done}\nShifts found: {self.shiftCount}\nScan interval: {self.interval}s\nShift load timeout: {self.timeout}s\nCurrently scanning: {self.doAutoScan}", parse_mode=ParseMode.MARKDOWN)

    async def cmd_timeout(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id not in authorized:
            await update.message.reply_text(f"Not authorized to use this command. (Originally from: {update.effective_user.full_name}\nID: {update.effective_user.id})")
            return
        if len(context.args) != 1:
            await update.message.reply_text("Usage: /timeout <seconds>")
            return
        old = self.timeout
        self.timeout = float(context.args[0])
        await update.message.reply_text(f"⏱ Timeout changed: {old}s → {self.timeout}s")
    
    async def cmd_patchnotes(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(f"Version 1.2.0\n + Added timeout command\n + Added patch notes command\n ? Fixed/Switched to work with OneLogin MFA app instead of SMS",
                                        parse_mode=ParseMode.MARKDOWN)

    async def cmd_publish(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id not in authorized:
            await update.message.reply_text(f"Not authorized to use this command. (Originally from: {update.effective_user.full_name}\nID: {update.effective_user.id})")
            return
        if self.shiftCount == 0:
            await self.message_priority("No shifts to publish.")
            return
        await self.message_priority("Published shifts to the main channel!")
        await self.message_all(f"🚨 *New Shifts Detected!* (Count: {self.shiftCount})")