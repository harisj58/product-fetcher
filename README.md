# Product Fetcher

A FastAPI-based microservice to fetch and structure product data from Bing Shopping (via SerpAPI) for any supported country. It returns a clean, uniform JSON of product offers, including external links and seller details, for a given search query and country code.

⚠️ **IMPORTANT:** This code was intended to run on Linux platform. Might have issues with other OSes.

## Features

- Fetches product offers from Bing Shopping using SerpAPI

- Supports hundreds of country codes

- Returns structured, uniform JSON output

- Cleans and normalizes product data (name, price, seller, etc.)

- Dockerized for easy deployment

## Requirements

- Python 3.12+

- [SerpAPI](https://serpapi.com/) API key (for Bing Shopping)

- [uv](https://docs.astral.sh/uv/getting-started/installation/) for dependency management (Optional, but recommended)

- [Playwright](https://playwright.dev/python/) (installed automatically)

## Setup

1.  **Clone the repository:**

```bash

git clone <repo-url>

cd product-fetcher

```

2.  **Install dependencies:**

```bash

uv sync

```

3.  **Activate the virtual environment:**

```bash

source .venv/bin/activate

```

Alternatively, you could create a regular python virtual environment and use `requirements.txt` to install dependencies.

4.  **Install Playwright browsers:**

This may require sudo privilege:

```bash

playwright install --with-deps

```

4.  **Set up environment variables:**

Create a `.env` file in the root directory with (refer to `.env.example`):

```env

SERP_API_KEY=your_serpapi_key_here

```

5.  **Run the server:**

```bash

poetry run uvicorn server:app --reload

```

The API will be available at `http://localhost:8000`.

## Docker

To build and run with Docker:

```bash

docker  build  -t  product-fetcher  .

docker  run  -p  8000:8000  --env  SERP_API_KEY=your_serpapi_key_here  MISTRAL_API_KEY=your_mistral_api_key_here product-fetcher

```

## API Endpoints

### Health Check

- **GET** `/health`

- **Response:**

```json
{ "status": "ok", "message": "Server is running!" }
```

### Product Search

- **POST** `/search`

- **Request Body:**

```json
{
  "country": "US",

  "query": "iPhone 16 Pro 128GB"
}
```

- **Response:** (example)

```json
[
  {
    "link": "https://www.bestbuy.com/site/apple-iphone-16-pro-128gb-apple-intelligence-desert-titanium-verizon/6443356.p?affgroup=%22Content%22",

    "price": "$27.77",

    "currency": "USD",

    "productName": "Apple iPhone 16 Pro",

    "seller": "Best Buy",

    "otherDetails": {}
  },

  {
    "link": "https://www.amazon.com/dp/B0DHSZNGZ5",

    "price": "$1,199.96",

    "currency": "USD",

    "productName": "iPhone 16 Pro",

    "seller": "Amazon",

    "otherDetails": {}
  }
]
```

- **Error Response:**

```json
{ "status": "error", "message": "Some error occurred for your request - ..." }
```

## Supported Countries

The `country` field must be a valid [ISO 3166-1 alpha-2 country code](https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes). See `country_codes.txt` for the full list. Examples: `US`, `IN`, `JP`, `DE`, etc.
