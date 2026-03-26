# ANeT SelfService Shift Bot
Scans for available shifts on the ANeT SelfService website (used by big organizations like TESCO etc...) and alerts a telegram chat/groupchat if some available shifts are found. Compatible with OneLogin MFA, fully controlled by commands via telegram chat, and much more...

# What is this? Why this exists? Is this moral? Can I get in trouble for using this?
Q: What is this?
A: A bot that automates human actions and saves someones time since the constant checking of shifts handles the bot more consistently and efficiently.

Q: Why this exists?
A: Started as a simple project of mine since I wanted to work more and earn more money, but I did not have the time to refresh the available shifts page every half a hour. I ended up expanding and giving it to some trusted friends that used this and got many work hours thanks to this bot

Q: Is this moral?
A: Short answer, hell no. Long answer, it automates what I would have done manualy but

# ! Example of .env file ! REQUIRED TO WORK AS PLUG AND PLAY !
Create a file named `.env` in the same directory as main.py is placed.
Here is what the file should contain:
```
USER="YOUR_USERNAME_FOR_ANET"
PWD="YOUR_PASSWORD_FOR_ANET"
TOKEN="YOUR_TELEGRAM_BOT_TOKEN"
CHAT_ID="MAIN_GROUPCHAT"
PRIORITY_ID="PRIORITY_GROUPCHAT"
MFA_ID="CHAT_ID_WHERE_MFA_CODES_SHOULD_BE_SENT_(YOUR_DMS_WITH_THE_BOT)"
```
The username and password are specified and given to you by your organization.
Token can be acquired [BotFather](https://help.superchat.com/en/articles/14901-how-do-i-get-the-telegram-token-or-bot-id) for example or some other methods which can be found online.
Main Chat ID can be acquired by ANeT Bot itself using `/id` command. This chat is for larger group of people (when 10 people have access to this bot but only few are "admins")
Priority Chat ID can be acquired the same way as before... The initial alert that there are available shifts with arrive here, after executing `/publish` command in this chat the shifts will be announced to the main group chat. This is to make sure selected people are guaranteed to get the shifts first.
MFA Chat ID is ID of the private chat between you and the bot only.
