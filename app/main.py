from fastapi import FastAPI
from app.api.v1.internet_search import router as internet_search_api
from app.api.v1.content_scraper import router as content_scraper_api

app = FastAPI()

app.include_router(internet_search_api, prefix="/api/v1")
app.include_router(content_scraper_api, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)