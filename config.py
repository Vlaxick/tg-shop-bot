import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ADMIN_IDS = [int(admin_id) for admin_id in os.getenv("ADMIN_IDS", "0").split(",") if admin_id.strip().isdigit()]

# Add your ID here manually for testing if you don't use .env
if not ADMIN_IDS or ADMIN_IDS[0] == 0:
    ADMIN_IDS = [5927166969] # vlaioxss
