from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app=FastAPI()
# <a href="{{ url_for('read_item', id=id) }} in base.html can also be used

# Set up templates and static file directories
templates=Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get('/',response_class=HTMLResponse)
def read_root(request:Request):
    return templates.TemplateResponse("index.html", {"request": request, "title": "Home Page", "message": "Welcome to FastAPI with Templates!"})

@app.get("/about", response_class=HTMLResponse)
def about_page(request: Request):
    # Render the base.html template with custom content
    return templates.TemplateResponse("base.html", {"request": request, "title": "About Us", "content": "This is the about page of our FastAPI app."})
