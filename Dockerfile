FROM python:3.11-slim

WORKDIR /app

# Install system dependencies and fonts
RUN apt-get update && apt-get install -y \
    fonts-dejavu-core \
    fonts-dejavu \
    fonts-liberation \
    fontconfig \
    && fc-cache -f -v \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port (optional, for health checks)
EXPOSE 8000

# Run the bot
CMD ["python", "main.py"]