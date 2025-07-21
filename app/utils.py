import re

def clean_message(content):
    """
    Cleans up incoming Discord messages for processing.
    - Strips leading/trailing spaces
    - Removes bot mentions
    """
    content = content.strip()
    # Remove bot mentions
    content = re.sub(r'<@!?\\d+>', '', content)
    return content
