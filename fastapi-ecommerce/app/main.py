from fastapi import FastAPI, HTTPException, Query, Path,Depends,Request
from service.products import load_products,get_all_products,add_product,remove_product,change_product
from schema.product import Product, ProductUpdate
from uuid import uuid4,UUID
from datetime import datetime
from typing import Dict,List
from dotenv import load_dotenv
import os
load_dotenv()
app = FastAPI()

# @app.middleware("http")
# async def lifecycle(request: Request,call_next):
#     print("before request")
#     response=await call_next(request)
#     response["lifecycle"]="was inside"
#     print("after request")
#     return response
    


def common_logic():
    print( "HELLO THERE" )
    return "HELLO THERE"
@app.get("/")
def root(dep=Depends(common_logic)):
    DB_PATH=os.getenv("BASE_URL")
    return {"message": "welcome to fast api","dependencies":dep,"data_path":DB_PATH}

@app.get("/products",response_model=Dict)
def list_products(   
    dep=Depends(load_products),
    name: str = Query(
        default=None,
        min_length=1,
        max_length=50,
        description="search by product name (case insensitive)",
    ),
    sort_by_price: bool =Query(
        default=False,
        description="sort products by price in ascending order"),
    order:str=Query(default="asc",
                    description="SORT ORDER WHEN sort_by_price=true(asc,desc)"),
    limit :int = Query(
        default=10,
        ge=1,
        le=100,
        description="maximum number of products to return",
    ),
    offset:int = Query(
        default=0,
        ge=0,
        description="number of products to skip before starting to collect the result set",
    ),
):
    products=dep

    if name:
        needle = name.strip().lower()
        products = [
            p for p in products
            if needle in p.get("name", "").lower()
        ]

    if not products:
        raise HTTPException(
            status_code=404,
            detail="no products found matching the search criteria"
        )
    if sort_by_price:
        reverse=order=="desc"
        products=sorted(products,key=lambda p:p.get("price",0),reverse=reverse)

    total = len(products)
    products = products[offset:offset+limit]

    return {
        "total": total,
        "limit": limit,
        "items": products
    }

@app.get("/products/{product_id}",response_model=Dict)
def get_product_id(
    product_id: str= Path(
        ...,
        min_length=36,
        max_length=36,
        description="UUID of the products",
        examples=["394d40e7-2a95-445d-8738-c6af6be5a97e"],
    )
):
    products= get_all_products()
    for product in products :
        if product["id"]==product_id:
            return product
    raise HTTPException(status_code=404,detail="Product not found!")


@app.post("/products",status_code=201)
def create_product(product: Product):
    product_dict=product.model_dump(mode="json")
    
    product_dict["id"]=str(uuid4())
    product_dict["created_at"]=datetime.utcnow().isoformat()+"Z"
    try:
        add_product(product_dict)
    except ValueError as e:
        raise HTTPException(status_code=400,detail=str(e))
    return product.model_dump(mode="json")

@app.delete("/products/{product_id}")
def delete_product(product_id:UUID= Path(...,description="Product_id")): 
    try:
        res=remove_product(str(product_id))
    except Exception as e:
        raise HTTPException(status_code=400,detail=str(e))
    return res
    

@app.put("/products/{product_id}")
def update_product(product_id:UUID= Path(...,description="Product UUID"),
                   payload:ProductUpdate=...,
                   ):
    try :
        update_product=change_product(str(product_id),payload.model_dump(mode="json",exclude_unset=True))
        return update_product
    except ValueError as e:
        raise HTTPException(status_code=404,detail=str(e))

