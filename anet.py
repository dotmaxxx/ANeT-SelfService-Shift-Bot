import os
import asyncio
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from dotenv import load_dotenv


class Driver:
    def __init__(self):
        load_dotenv()
        self.user = os.getenv("USER")
        self.pwd = os.getenv("PWD")
        self.pending_code = None
        self.bot = None  # set later via bot.setDriver()
        
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--use-gl=swiftshader")
        options.add_argument("--disable-background-networking")
        options.add_argument("--disable-features=PushMessaging")
        options.add_argument("--disable-gcm")
        options.add_argument("--disable-notifications")
        options.add_argument("--log-level=3")
        options.add_argument("--silent")

        self.driver = webdriver.Chrome(options=options)
        self.driver.get("https://anetskselfservice.ourtesco.com/selfservice/#/")
        self.driver.implicitly_wait(5.0)

    def setBot(self, bot):
        """Link the Telegram bot instance to this driver."""
        self.bot = bot

    async def _async_wait(self, seconds: float):
        await asyncio.sleep(seconds)

    async def isLoggedIn(self) -> bool:
        """Check if the Tesco Self Service dashboard is currently logged in."""
        await asyncio.to_thread(
            self.driver.get, "https://anetskselfservice.ourtesco.com/selfservice/#/dashboard"
        )
        await self._async_wait(3)
        try:
            await asyncio.to_thread(self.driver.find_element, By.CLASS_NAME, "_toolbar_1jbk1_1")
        except Exception:
            return False
        return True

    async def login(self) -> bool:
        """Perform login, including handling MFA via Telegram bot."""
        await asyncio.to_thread(self.driver.get, "https://anetskselfservice.ourtesco.com/selfservice/#/")
        loginButton = await asyncio.to_thread(self.driver.find_element, By.CSS_SELECTOR, "button")
        await asyncio.to_thread(loginButton.click)
        await self._async_wait(2)

        try:
            # Try normal username/password login
            userField = await asyncio.to_thread(self.driver.find_element, By.ID, "username")
            await asyncio.to_thread(userField.send_keys, self.user)
            await asyncio.to_thread(userField.send_keys, Keys.RETURN)
            await self._async_wait(2)

            pwdField = await asyncio.to_thread(self.driver.find_element, By.ID, "password")
            await asyncio.to_thread(pwdField.send_keys, self.pwd)
            await asyncio.to_thread(pwdField.send_keys, Keys.RETURN)
        except Exception:
            print("Logged back in without credentials...")

        try:
            # Check if MFA page is present
            await asyncio.to_thread(
                self.driver.find_element,
                By.XPATH,
                '//html/body/div/div/div/div/div/div/div/div/div/span/span'
            )

            
            print("Waiting for MFA code via Telegram...")

            # Send MFA alert to Telegram
            if self.bot:
                mfaReqCode = await asyncio.to_thread(self.driver.find_element, By.XPATH, '//*[@id="root"]/div/div/div[2]/div[1]/div[3]/div/div[2]/div/div[2]/div')
                #print(mfaReqCode.text)
                await self.bot.mfa_alert(
                    f"**⚠️ MFA Required!**\n`Confirm via OneLogin app with code: {mfaReqCode.text}`"
                )

                # Wait up to 120 seconds for MFA code
                for _ in range(120):
                    try:
                        mfaReqCode = await asyncio.to_thread(self.driver.find_element, By.XPATH, '//*[@id="root"]/div/div/div[2]/div[1]/div[3]/div/div[2]/div/div[2]/div')
                    except Exception:
                        print("Logged in...")
                        await self.bot.mfa_alert("✅ Logged in.")

                        break
                    await asyncio.sleep(1)
            else:
                print("2FA code not confirmed. Login will fail.")
                if self.bot:
                    await self.bot.mfa_alert("⚠️ 2FA code not confirmed. Login will fail.")
        except Exception as e:
            print(f"No 2FA required")
            #print(e)

        return True

    async def getShifts(self) -> int:
        """Navigate to the Free Shifts page and count available shifts."""
        if not await self.isLoggedIn():
            #if self.bot:
                #await self.bot.log("🔐 Session expired — logging in again...")
            await self.login()
            await self._async_wait(10)

        if not await self.isLoggedIn():
            await self.bot.log("🔐 Session expired — trying again in set interval...")
            return self.bot.shiftCount
        await asyncio.to_thread(
            self.driver.get,
            "https://anetskselfservice.ourtesco.com/selfservice/?#/freeshifts"
        )
        await self._async_wait(self.bot.timeout)

        elements = await asyncio.to_thread(
            self.driver.find_elements, By.CLASS_NAME, "_shift_1ai1e_88"
        )

        count = len(elements) // 2  # same as original
        #if self.bot:
            #await self.bot.log(f"📊 Found {count} shifts on Free Shifts page.")
        return count
