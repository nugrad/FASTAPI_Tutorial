from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Setting up templates
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def show_form(request: Request):
    """
    Display the input form to the user.
    """
    return templates.TemplateResponse("form.html", {"request": request})

@app.post("/submit", response_class=HTMLResponse)
async def process_form(request: Request, name: str = Form(...), age: int = Form(...)):
    """
    Process form data submitted by the user.
    """
    message = f"Hello, {name}! You are {age} years old."
    return templates.TemplateResponse("result.html", {"request": request, "message": message})
