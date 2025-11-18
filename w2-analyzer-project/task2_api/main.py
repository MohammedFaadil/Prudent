from fastapi import FastAPI
import sys
import os

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from task2_api.routes import price_gap, movies

app = FastAPI(
    title="Price Gap & Movies API",
    description="API for finding price gap pairs and searching movies",
    version="1.0.0"
)

# Include routers
app.include_router(price_gap.router, prefix="/api", tags=["price-gap"])
app.include_router(movies.router, prefix="/api", tags=["movies"])

@app.get("/")
async def root():
    return {"message": "Price Gap & Movies API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)