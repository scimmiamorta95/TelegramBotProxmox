from config import AUTHORIZED_USERS
from proxmox_utils import (
    get_all_vms_status,
    start_vm_or_container,
    stop_vm_or_container,
    restart_vm_or_container,
    test_connection
)
import logging

logger = logging.getLogger(__name__)

bot = None  # Questo verrà inizializzato in bot.py


def is_authorized(chat_id):
    return str(chat_id) in AUTHORIZED_USERS


def handle(msg):
    global bot
    chat_id = msg['chat']['id']
    text = msg.get('text', '').strip()

    if not text.startswith('/'):
        bot.sendMessage(chat_id, "Command not recognised. Start with '/'.")
        return

    command_parts = text[1:].split()
    if not command_parts:
        bot.sendMessage(chat_id, "Empty command.")
        return

    command = command_parts[0].lower()
    args = command_parts[1:]

    logger.info(f"Received command: {command} {' '.join(args)} from {chat_id}")

    if not is_authorized(chat_id):
        bot.sendMessage(chat_id, "ACCESS DENY.")
        return

    if command in ("status", "list"):
        status = get_all_vms_status()
        bot.sendMessage(chat_id, status)

    elif command == "start":
        if not args:
            bot.sendMessage(chat_id, "Correct using /start <vmid>")
            return
        vmid = args[0]
        success, message = start_vm_or_container(vmid)
        bot.sendMessage(chat_id, message)

    elif command == "stop":
        if not args:
            bot.sendMessage(chat_id, "Correct using: /stop <vmid> [force]")
            return
        vmid = args[0]
        force = len(args) > 1 and args[1].lower() == "force"
        success, message = stop_vm_or_container(vmid, force)
        bot.sendMessage(chat_id, message)

    elif command == "forcestop":
        if not args:
            bot.sendMessage(chat_id, "Correct using: /forcestop <vmid>")
            return
        vmid = args[0]
        success, message = stop_vm_or_container(vmid, force=True)
        bot.sendMessage(chat_id, f"{message} (FORZATO)")

    elif command == "restart":
        if not args:
            bot.sendMessage(chat_id, "Correct using: /restart <vmid>")
            return
        vmid = args[0]
        success, message = restart_vm_or_container(vmid)
        bot.sendMessage(chat_id, message)

    elif command == "ping":
        success, message = test_connection()
        bot.sendMessage(chat_id, message)

    else:
        bot.sendMessage(chat_id,
            "AVAILABLE COMMANDS:\n\n"
            "/status – Status of all VM/LXC\n"
            "/start <vmid>\n"
            "/stop <vmid> [force]\n"
            "/forcestop <vmid>\n"
            "/restart <vmid>\n"
            "/ping"
        )
