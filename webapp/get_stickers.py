import re
import urllib.request

# Let's try to fetch a sticker pack page that has Telegram gifts
url = "https://chpic.su/en/stickers/TelegramGifts/"
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    html = urllib.request.urlopen(req).read().decode('utf-8')
    matches = re.findall(r'https://[^"]+\.webp', html)
    print("Found:", len(matches))
    for m in matches[:10]:
        print(m)
except Exception as e:
    print(e)
