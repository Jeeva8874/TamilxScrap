from os import getenv as genv
from pyrogram import Client

API_ID = genv("API_ID", "22977776")

API_HASH = genv("API_HASH", "2ac7223d720bdeec757cbc88ced57224")

BOT_TOKEN = genv("BOT_TOKEN", "7692272341:AAEcqZkFIx6Y6iljv96xt3SXSNwGY4_V8O4")

SUPPORT_GROUP = genv("SUPPORT_GROUP", "TGHelpingGroup")

UPDATES_CHANNEL = genv("UPDATES_CHANNEL", "PlayTamilX")

GROUP_ID = int(genv("GROUP_ID", "-1002341945360"))  # add group id where your leech is added

DATABASE_URL = genv(
    "DATABASE_URL",
    "mongodb+srv://jeevanantham8157:1055221@leechbot.gpkuo.mongodb.net/?retryWrites=true&w=majority&appName=Leechbot",
)

USER_SESSION_STRING = genv(
    "USER_SESSION_STRING",
    "BQFenPAAxwowyQ1289EiQZkXKhK2kVcM7wqu6XD5w8IB45uuFhFz3tYA6GjzaskOBBDzc3afhVcyFqqzFaZJTNkD8ewXs4l0utCOa0XDIJ8BpaQOKHRvGMW0hadA4yMlTsKfSXIazs5n6Wyv0ELS_MMmwv8mxFdTIgmWZWhOWstXQvc-fifrkMjcx1zpj6SwnETcUsgNTy5TAi_13_FLO3yA3hAXB6mEs9H22LlXjQSYr1Rd7-bJ2iwNyfuEK4-0zDBcW8JlxQ-_GPieLFLhAZPJyZUxD3mFMKRQKiktxTB9s2CW_LA4t8xjyxDxJz-WiXrXboP3prFymy_7AsQY2p6hbBB3FQAAAAGTFHWXAA",
)

SERVER_URL = genv("SERVER_URL", "https://tamilxscrap.koyeb.app/")


RSS_CHAT = int(
    genv("RSS_CHAT", "-1002335041395")
)  # add the channel id where the torrent files need to be sent

BASE_URL = genv(
    "BASE_URL", "https://www.1tamilmv.fit"
).lower()  # update the main domain if changed



#change the theme as you required



START_TXT = """<b>Hello {}, I am a Scrapper Bot!.
๏ I can scrap links from 1tamilmv and update it in Bot..
๏ Click on the help menu button below to get information about my commands.
๏ Powered By @TamilXLeech</b>"""


HELP_TXT = """Send any Movie Name and I will provide torrent links.

Available Commands

-> /get - To Get Torrent Link of that Movie
-> /list - To get last 10 Movie/Series details

Updates - ⍟ @MadxBotz"""

ABOUT_TXT = """<b>╔════❰ Tʙ Sʜᴏʀᴛɴᴇʀ Bᴏᴛ ❱═══❍
║ ┏━━━━━━━━━❥
║ ┣ Mʏ ɴᴀᴍᴇ -> {}
║ ┣ Uᴘᴅᴀᴛᴇꜱ -> <a href="tg://TamilXLeech">••Bᴏᴛs••</a>
║ ┣ 𝖲ᴜᴘᴘᴏʀᴛ -> <a href="tg://TGHelpingGroup"> Bᴏᴛs Sᴜᴩᴩᴏʀᴛ</a>
║ ┣ ๏ Cʜᴇᴄᴋ ʜᴇʟᴘ ᴛᴏ ᴋɴᴏᴡ ᴍᴏʀᴇ.
║ ┗━━━━━━━━━❥
╚═════❰ @ ❱═════❍</b>"""


RELEASES_PATH = genv("RELEASES_PATH", "/index.php?/forums/topic/")  # dont change this
