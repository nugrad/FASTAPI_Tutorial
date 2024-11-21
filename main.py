from fastapi import FastAPI
app=FastAPI()

@app.get('/')
def index():
   return {"data":{"name":"hamza"}}
@app.get('/about')
def about():
   return {"data":"this is the about Page"}