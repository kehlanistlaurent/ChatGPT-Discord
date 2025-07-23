import re

def clean_message(content, bot_id=None):
    """
    Cleans up incoming Discord messages for processing.
    - Strips leading/trailing spaces
    - Removes bot mentions
    """
    content = content.strip()
    if bot_id:
        content = re.sub(rf'<@!?{bot_id}>', '', content)
    else:
        content = re.sub(r'<@!?\d+>', '', content)
    return content.strip()
