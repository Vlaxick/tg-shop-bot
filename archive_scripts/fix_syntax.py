with open("/Users/macbook/tg-bot/handlers/user_handlers.py", "r") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if line.strip() == '"' or line.strip() == 'f"🔗 <b>Ваше реферальне посилання:</b>':
        continue
    new_lines.append(line.replace('"\n', '\\n"\n') if line.strip().startswith('"') and not line.strip().endswith(')') else line)

# let's just rewrite the process_referrals function
