with open("/Users/macbook/tg-bot/handlers/admin_handlers.py", "r") as f:
    content = f.read()

import re
content = content.replace('text=f"🎉 <b>Бонус від реферала!</b>\nВаш друг щойно здійснив покупку!\nВам нараховано <b>{cashback} ₴</b> кешбеку <i>[{cb_type}]</i>.",', 'text=f"🎉 <b>Бонус від реферала!</b>\\nВаш друг щойно здійснив покупку!\\nВам нараховано <b>{cashback} ₴</b> кешбеку <i>[{cb_type}]</i>.",')

with open("/Users/macbook/tg-bot/handlers/admin_handlers.py", "w") as f:
    f.write(content)
