FROM python:3.12-slim

WORKDIR /app

# Install system dependencies + xvfb for headed Playwright
RUN apt-get update && apt-get install -y build-essential curl libssl-dev libffi-dev xvfb && rm -rf /var/lib/apt/lists/*

# Install Python dependencies + Playwright
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt && playwright install --with-deps

# Copy project files
COPY . .

EXPOSE 8000

# Start FastAPI with headed Playwright using Render's $PORT
CMD ["sh", "-c", "xvfb-run --auto-servernum --server-args='-screen 0 1920x1080x24' uvicorn server:app --host 0.0.0.0 --port $PORT"]
