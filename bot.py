from telepot import Bot
from handlers import handle
from config import TELEGRAM_TOKEN
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(TELEGRAM_TOKEN)
bot.message_loop(handle)

logger.info("Proxmox Bot started...")

while True:
    time.sleep(1)
