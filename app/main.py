from fastapi import FastAPI

from app.api.routes import router

app = FastAPI()
app.include_router(router)


@app.get("/")
async def read_root():
    return {"message": "Welcome to the Document Interpolation API"}
