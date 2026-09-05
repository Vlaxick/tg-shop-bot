with open("/Users/macbook/tg-bot/handlers/user_handlers.py", "r") as f:
    content = f.read()

if "from aiogram import Bot" not in content:
    content = content.replace("from aiogram import Router, F", "from aiogram import Router, F, Bot")

with open("/Users/macbook/tg-bot/handlers/user_handlers.py", "w") as f:
    f.write(content)
