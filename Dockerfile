# Base image
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot files
COPY app/ ./app/
COPY .env .env

# Run the bot
CMD ["python", "app/bot.py"]
