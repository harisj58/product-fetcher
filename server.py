from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
def health_check():
    resp = {
        "status": "ok",
        "message": "Server is running!",
    }
    return resp
