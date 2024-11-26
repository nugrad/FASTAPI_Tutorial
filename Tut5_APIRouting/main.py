from fastapi import FastAPI

from .routers import author
from .routers import blog
from .database import engine
from . import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
# run using the command
# C:\Users\Dell\Desktop\FASTAPI_SERIES>uvicorn Tut5_APIRouting.main:app --reload

# Register Routers
app.include_router(blog.router)
app.include_router(author.router)
