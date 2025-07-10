FROM python:3.12-slim

WORKDIR /app

# Install system packages
RUN apt-get update && apt-get install -y curl build-essential libssl-dev libffi-dev xvfb && rm -rf /var/lib/apt/lists/*

# Install uv
ENV PATH="/root/.local/bin:$PATH"

RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Copy only dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies and create .venv
RUN uv sync

# Activate virtual environment and install playwright browsers
RUN .venv/bin/python -m playwright install --with-deps

# Copy the app code
COPY . .

EXPOSE 8000

# Activate .venv and run the app using xvfb
CMD ["/bin/sh", "-c", ". .venv/bin/activate && xvfb-run --auto-servernum --server-args='-screen 0 1920x1080x24' uvicorn server:app --host 0.0.0.0 --port $PORT"]
