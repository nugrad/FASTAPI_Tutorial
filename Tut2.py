# Tutorial # 2 : Request Body and CRUD Operations
from fastapi import FastAPI,status,HTTPException
from typing import Optional
from pydantic import BaseModel

app=FastAPI()
# When you need to send data from a client (let's say, a browser) to your API, you send it as a request body.
#A request body is data sent by the client to your API. A response body is the data your API sends to the client.
# Your API almost always has to send a response body. But clients don't necessarily need to send request bodies all the time, 
# sometimes they only request a path, maybe with some query parameters, but don't send a body.
#To declare a request body, you use Pydantic models with all their power and benefits

class Item(BaseModel):
    name:str
    description:Optional[str]=None
    # description: str | None = None
    price:float
    tax:float|None=None

# Now we will apply some crud operations on it
# @app.post('/items/')
# def create_item(item:Item):
#     item_dict = item.dict()
#     if item.tax:
#         price_with_tax = item.price + item.tax
#         item_dict.update({"price_with_tax": price_with_tax})
#     return item_dict
items = {}  # In-memory storage for demonstration
# adding the item
@app.post('/items/{item_id}')
def create_item(item_id:int,item:Item):
    if item_id in items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="item id  already exist")
    items[item_id]=item
    return{"item_id":item_id,**item.dict(),"price_with_tax": item.price + (item.tax or 0)}

# updating the item
@app.put('/items/{item_id}')
def update_item(item_id:int,item:Item):
    if item_id not in items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="item name not found")
    
    items[item_id] = item  # Update the existing item
    return {"item_id": item_id, **item.dict(),"price_with_tax": item.price + (item.tax or 0)}

# deleting an item
@app.delete('/items/{item_id}')
def delete_item(item_id:int,item:Item):
    if item_id not in items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="item  not found")
    
    # del items[item_id]
    # return {"message": "Item deleted successfully"}
    deleted_item = items.pop(item_id)
    return {"message": "Item deleted successfully",**deleted_item.dict(), "price_with_tax": deleted_item.price + (deleted_item.tax or 0)}

# Get an Item
@app.get('/items/{item_id}')
def get_item(item_id:int):
    if item_id not in items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="item name not found")
    
    item=items[item_id]
    return{"item_id":item_id,**item.dict(),"price_with_tax": item.price + (item.tax or 0)}



    

