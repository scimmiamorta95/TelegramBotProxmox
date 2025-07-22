import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
AUTHORIZED_USERS = [int(x) for x in os.getenv("AUTHORIZED_USERS", "").split(",") if x]

PROXMOX_HOST = os.getenv("PROXMOX_HOST")
PROXMOX_USER = os.getenv("PROXMOX_USER")
PROXMOX_TOKEN_NAME = os.getenv("PROXMOX_TOKEN_NAME")
PROXMOX_TOKEN_VALUE = os.getenv("PROXMOX_TOKEN_VALUE")
VERIFY_SSL = os.getenv("VERIFY_SSL", "False").lower() in ["true", "1", "yes"]

TIMEOUT = int(os.getenv("TIMEOUT", "10"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "5"))
RETRY_DELAY = int(os.getenv("RETRY_DELAY", "2"))
CONNECTION_CACHE_DURATION = int(os.getenv("CONNECTION_CACHE_DURATION", "10"))
