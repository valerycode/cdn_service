import uvicorn

from src.config import app
from src.api.v1 import media

app.include_router(media.router)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
