# Tutorial 1 : Basics, Path and Query Parameters
from fastapi import FastAPI,Path,Query
from typing import Optional
app=FastAPI()

Blogs={
   1:{
      "name":"8 Skills to Master in NLP",
      "author":"Hamza Jafri"
   },
   2:{
      "name":"Data Manipulation with Pandas and Numpy",
      "author":"Bilal Mamji"

   }
}
@app.get('/')
def index():
   return {"data":"This the Home Page"}

#  Now Lets Learn  about Path Parameters, import Path Module
# lets get to the basics
# @app.get("/items/{item_id}")
# def read_item(item_id):
#     return {"item_id": item_id} 
# http://127.0.0.1:8000/items/foo , gives {"item_id":"foo"}

# You can declare the type of a path parameter in the function
@app.get("/items/{item_id}")
def read_item(item_id:int):
    return {"item_id": item_id}
# http://127.0.0.1:8000/items/1, gives {"item_id":1}


# Keep in mind, the order matters
# When creating path operations, you can find situations where you have a fixed path, like /users/me,
# let's say that it's to get data about the current user.
# And then you can also have a path /users/{user_id} to get data about a specific user by some user ID.
# Because path operations are evaluated in order, you need to make sure that the path for /users/me 
# is declared before the one for /users/{user_id}
@app.get("/users/me")
def read_user_me():
    return {"user_id": "the current user"}


@app.get("/users/{user_id}")
def read_user(user_id: str):
    return {"user_id": user_id}

# Otherwise, the path for /users/{user_id} would match also for /users/me, 
# "thinking" that it's receiving a parameter user_id with a value of "me".
# Similarly, you cannot redefine a path operation



@app.get('/get-blog/{blog_id}')
def get_blog(blog_id:int=Path(description="Blog you requested",gt=0)):

   return Blogs[blog_id]

# ------------------------------
# Now Lets Learn about Query parameters, import Query Module

# When you declare other function parameters that are not part of the path parameters, 
# they are automatically interpreted as "query" parameters.
# The query is the set of key-value pairs that go after the ? in a URL, separated by & characters.
# query parameters can be optional and can have optional values
# in the below example both skip and and limit have default values of 0 and 10 respectively
fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


@app.get("/db-items/")
def read_item(skip: int = 0, limit: int = 10):
    return fake_items_db[skip : skip + limit]
# http://127.0.0.1:8000/db-items/ is same as http://127.0.0.1:8000/items/?skip=0&limit=10
# similary http://127.0.0.1:8000/db-items/?skip=0&limit=2, gives [{"item_name":"Foo"},{"item_name":"Bar"}]

# Also we can have optional path parameters, whether we pass it or not , it does not matters

@app.get("/op-items/{item_id}")
async def read_item(item_id: str, q:Optional[str]=None):
    if q:
        return {"item_id": item_id, "q": q}
    return {"item_id": item_id}
# http://127.0.0.1:8000/op-items/1?q=optional , gives {"item_id":"1","q":"optional"}

# we can also have required query param, without which route wont work and give error
#below needy is the required query parameter of type str
# without giving needy ,it gives following error
# {"detail":[{"type":"missing","loc":["query","needy"],"msg":"Field required","input":null}]}
# http://127.0.0.1:8000/req-items/one?needy=veryneeddy
@app.get("/req-items/{item_id}")
async def read_user_item(item_id: str, needy: str):
    item = {"item_id": item_id, "needy": needy}
    return item

#-------------------------------------
# Now that we have knowledge of both path and query param , lets use them together, though we have seen it earlier as well
# Multiple path and query parameters
#http://127.0.0.1:8000/item-user/1/users-items/mobile?q=Galaxy%20S24%20Ultra&short=False
#{"item_id":"mobile","owner_id":1,"q":"Galaxy S24 Ultra","description":"This is an amazing item that has a long description"}

@app.get("/item-user/{user_id}/users-items/{item_id}")
def read_user_item(
    user_id: int, item_id: str, q:Optional[str] = None, short: bool = False
):
    item = {"item_id": item_id, "owner_id": user_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item

# And of course, you can define some parameters as required, some as having a default value, and some entirely optional:
# @app.get("/items/{item_id}")
# def read_user_item(
#     item_id: str, needy: str, skip: int = 0, limit: Optional[str]= None):
#     item = {"item_id": item_id, "needy": needy, "skip": skip, "limit": limit}
#     return item
# ------------------------------------------------------
# Returning Something from our Blog Dictionary
@app.get('/get-by-name/{blog_id}')
def get_by_name(blog_id:int,name:str):
    for blog_id in Blogs:
        if Blogs[blog_id]["name"]==name:
            return Blogs[blog_id]
    return {"Data":"Blog not Found"}
# http://127.0.0.1:8000/get-by-name/1?name=8 Skills to Master in NLP
# {"name":"8 Skills to Master in NLP","author":"Hamza Jafri"}


   
   
   