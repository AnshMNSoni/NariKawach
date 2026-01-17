from fastapi import FastAPI
from src.api.endpoints import router
from src.api.middleware import AuthMiddleware

app = FastAPI(
    title="Nari Kawach ML Service",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

@app.get("/")
def root():
    return {"message": "ML service alive"}

app.add_middleware(AuthMiddleware)
app.include_router(router, prefix="/api/v1")
