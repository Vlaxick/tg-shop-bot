with open("/Users/macbook/tg-bot/keyboards/inline.py", "r") as f:
    content = f.read()

# I need to edit cabinet builder. I haven't seen `builder.as_markup()` inside user_handlers.py, I think it's done dynamically in `process_cabinet`.
