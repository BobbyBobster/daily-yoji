from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router as api_router
from app import create_flask_app

app = FastAPI()
# To enable Cordova requests
# TODO: Check if these permissions can be reduced
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router, prefix="/api/v1")

flask_app = create_flask_app()
app.mount("/", WSGIMiddleware(flask_app))
