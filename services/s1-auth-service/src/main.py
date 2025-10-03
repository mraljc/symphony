from fastapi import FastAPI
from src.api.endpoints import router as auth_router
from src.config.settings import settings

app = FastAPI(title="S1 Auth Service", version="1.0.0")

# Include routers
app.include_router(auth_router)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "S1 Auth Service"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)