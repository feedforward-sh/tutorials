import os
import re
import requests
from dotenv import load_dotenv
from fastmcp import FastMCP


def auto_link(content, titles):
    for title in sorted(titles, key=len, reverse=True):
        pattern = r'\b' + re.escape(title) + r'\b'
        link = f'[[{title}]]'
        content = re.sub(pattern, link, content)
    return content


load_dotenv()

mcp = FastMCP(name="ObsidianServer", stateless_http=True)


async def update_links():
    current_notes = requests.get(
        str(os.getenv('OBSIDIAN_SERVER_URL')) + "/",
        headers={
            "Authorization": f"Bearer {os.getenv('OBSIDIAN_API_KEY')}"},
            verify=False
        )
    current_notes = current_notes.json()
    current_notes_names = [note.split('.')[0].lower() for note in current_notes["files"]]
    headers = {
        "Authorization": f"Bearer {os.getenv('OBSIDIAN_API_KEY')}",
        "Content-Type": "text/plain"
    }
    for path in current_notes["files"]:
        url = f"{os.getenv('OBSIDIAN_SERVER_URL')}/{path.replace('/', '%2F')}"
        response = requests.get(url, headers=headers, verify=False)
        content_relinked = auto_link(response.text, current_notes_names)
        response = requests.put(
            url,
            headers=headers,
            data=content_relinked.encode('utf-8'),
            verify=False
        )


# 2.2 Register an async tool to return the current time
@mcp.tool()
async def create_note(title: str, content: str) -> str:
    """Create a new note in the Obsidian vault and link it to existing notes."""
    note_path = f"{title}.md"
    url = f"{os.getenv('OBSIDIAN_SERVER_URL')}/{note_path.replace('/', '%2F')}"

    # Send the POST request to create the note
    response = requests.put(
        url,
        headers={
            "Authorization": f"Bearer {os.getenv('OBSIDIAN_API_KEY')}",
            "Content-Type": "text/plain"
        },
        data=content.encode('utf-8'),
        verify=False  # local self-signed certs
    )

    if response.ok:
        await update_links()
        return f"Note created successfully at {url}"
    return f"Error: {response.status_code} {response.text}"



if __name__ == "__main__":
    # 2.3 Run synchronously in HTTP mode (concurrent clients supported)
    # Defaults: host=127.0.0.1, port=8000, path="/mcp/"
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=8000,
        path="/mcp/"
    )
