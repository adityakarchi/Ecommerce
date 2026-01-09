import json
from pathlib import Path
from typing import List,Dict

DATA_FILE=Path(__file__).parent.parent / "data" / "products.json"
def load_products() -> List[Dict]:
    if not DATA_FILE.exists():
        return []
    with open(DATA_FILE,"r",encoding="utf-8") as file:
        return json.load(file)
def get_all_products() -> List[dict]:
    return load_products()


def save_product(products: List[Dict])-> None:
    with open(DATA_FILE,"w",encoding="utf-8") as f:
        json.dump(products,f,indent=2,ensure_ascii=False)


##add
def add_product(product: Dict)->Dict :
    products=get_all_products()
    if any(p.get("sku")==product.get("sku") for p in products):
        raise ValueError("SKU alreaddy exist")
    products.append(product)
    save_product(products)
    return product
##delete
def remove_product(id:str)-> str:
    products=get_all_products()
    for idx ,p in enumerate(products):
        if p["id"]==str(id):
            deleted=products.pop(idx)
            save_product(products)
            return {"message":"Product deleted succesfully","data":deleted}

##update
def change_product(product_id:str,update_data: Dict):
    products=get_all_products()
    for index,product in enumerate(products):
        if product["id"]==product_id:
            for key,value in update_data.items():
                if value is None:
                    continue
                
                if isinstance(value,Dict) and isinstance(product.get(key),Dict):
                    product[key].update(value)
                else:
                    product[key]=value
            products[index]=product
            save_product(products)
            return product
        raise ValueError("product not found")