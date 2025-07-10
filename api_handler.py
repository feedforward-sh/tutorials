"""
I need to understand which endpoints are available via community plugin of Obsidian

https://github.com/obsidianmd/obsidian-api
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

# ⚙️ Set your API endpoint and key
API_URL = "http://localhost:27123/vault"
API_KEY = os.getenv("OBSIDIAN_API_KEY")

# 🎯 Target note path inside your vault
note_path = "testnote2.md"
url = f"{API_URL}/{note_path.replace('/', '%2F')}"

# Markdown content for the new note
content = (
    "Hello from the Obsidian REST API! 🎉"
    "Let's talk about lions with dolphins"
    "and [[testnote]]"
)

# Send the POST request to create the note
response = requests.put(
    url,
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "text/plain"
    },
    data=content.encode('utf-8'),
    verify=False  # local self-signed certs
)

if response.ok:
    print("✅ Note created successfully!")
else:
    print("❌ Error:", response.status_code, response.text)
