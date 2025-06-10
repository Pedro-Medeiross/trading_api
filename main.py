import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from connection import engine, SessionLocal
from routes.user_router import user_router

models_folder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')

all_files = os.listdir(models_folder_path)

exclude_files = ['__pycache__', 'base_model.py', '__init__.py', 'trades.py']

models_files = [file for file in all_files if file not in exclude_files]

models = [__import__(f'models.{file[:-3]}', fromlist=['']) for file in models_files]

for model in models:
    if hasattr(model, 'Base'):
        if hasattr(model.Base, 'metadata'):
            model.Base.metadata.create_all(engine)

app = FastAPI()

"""
origins = [
    "http://127.0.0.1:3000",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:34115"
    "http://localhost:5173"
]
"""

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router, prefix='/user', tags=['user'])