# Use official Python image
FROM python:3.12-slim

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential curl libssl-dev libffi-dev xvfb && rm -rf /var/lib/apt/lists/*

# Install pip, uvicorn, and poetry
RUN pip install --upgrade pip uvicorn[standard] poetry

# Install Playwright and browsers
RUN pip install playwright && playwright install --with-deps

# Copy project files
COPY . .

# Install Python dependencies
RUN poetry install --no-root --only main

# Expose port
EXPOSE 8000

# Run the FastAPI app with uvicorn
CMD ["xvfb-run", "--auto-servernum", "--server-args=-screen 0 1920x1080x24", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
