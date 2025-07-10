from fastapi import FastAPI
from schema.models import SearchRequest
from utils.search import search_google
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()


@app.get("/health")
def health_check():
    resp = {
        "status": "ok",
        "message": "Server is running!",
    }
    return resp


@app.post("/search")
async def search(request: SearchRequest):
    try:
        res = await search_google(request.query, request.country)
        return res
    except Exception as e:
        return {
            "status": "error",
            "message": f"Some error occurred for your request - {str(e)}",
        }
