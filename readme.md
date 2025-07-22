# Proxmox Telegram Bot

A **Telegram bot** written in Python to manage **virtual machines (VMs)** and **containers (LXC)** on a **Proxmox VE** cluster.

> Simple Telegram commands  
> Access restricted to authorized users  
> Compatible with local or remote Proxmox installations

---

## Features

- Start, stop, and restart VMs or containers  
- List the status of all VMs/LXCs  
- Support for multi-node Proxmox clusters  
- Authentication via Telegram user ID  
- Telegram commands like `/start`, `/stop`, `/status`, etc.

---

## Requirements

- Python 3.8+  
- A Proxmox VE with accessible API (with token)  
- A Telegram bot registered via [@BotFather](https://t.me/BotFather)

---

## Installation

### 1. Clone the project

```bash
git clone https://github.com/your-username/proxmox-telegram-bot.git
cd proxmox-telegram-bot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Create the `.env` file

Copy the example file:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```dotenv
TELEGRAM_TOKEN=123456:ABC-your-token
AUTHORIZED_USERS=123456789,987654321
PROXMOX_HOST=192.168.1.100
PROXMOX_USER=root@pam
PROXMOX_TOKEN_NAME=telegrambot
PROXMOX_TOKEN_VALUE=your-proxmox-api-token
VERIFY_SSL=False
```

### Start the bot

```bash
python bot.py
```

The bot will run in the background and you can start interacting with it on Telegram.

---

## 💬 Available Commands

| Command           | Description                           |
|-------------------|-------------------------------------|
| `/status`         | List all VMs/LXCs with status and type |
| `/start <vmid>`   | Start a VM or LXC                   |
| `/stop <vmid>`    | Gracefully stop a VM or LXC         |
| `/stop <vmid> force` | Force stop a VM or LXC            |
| `/forcestop <vmid>` | Alias for force stop               |
| `/restart <vmid>` | Restart a VM or LXC                 |
| `/ping`           | Test connection to the Proxmox server |

---

## 👤 Authorization

Only users whose Telegram IDs are listed in `AUTHORIZED_USERS` can use the bot.

To find your Telegram ID, you can use the [@userinfobot](https://t.me/userinfobot).

---

## 🛡️ Security

⚠️ Never commit your `.env` file with real credentials.

The `.gitignore` is already configured to ignore it.

---

## 📄 License

This project is distributed under the MIT License. Feel free to modify and share it.
