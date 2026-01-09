from pydantic import (
    BaseModel,
    Field,
    AnyUrl,
    field_validator,
    model_validator,
    computed_field,
    EmailStr,
)
from typing import Annotated, Literal, Optional, List
from uuid import UUID
from datetime import datetime
###create pydantic

# DIMENSIONS  

class DimensionCM(BaseModel):
    length: Annotated[float, Field(gt=0, description="Length in cm")]
    width: Annotated[float, Field(gt=0, description="Width in cm")]
    height: Annotated[float, Field(gt=0, description="Height in cm")]
    @computed_field
    @property
    def volume_cm3(self) -> float:
        return round(self.length * self.width * self.height, 2)

#  SELLER  
class Seller(BaseModel):
    id: UUID

    name: Annotated[
        str,
        Field(
            min_length=2,
            max_length=80,
            description="Seller name (2–80 chars)",
            examples=["Redmi Store", "Apple India"],
        ),
    ]

    email: EmailStr
    website: AnyUrl

    @field_validator("email", mode="after")
    @classmethod
    def validate_seller_email(cls, value: EmailStr):
        allowed_domains = ["mistore.in", "hpworld.in"]
        domain = str(value).split("@")[-1].lower()

        if domain not in allowed_domains:
            raise ValueError(f"Seller email domain not allowed: {domain}")

        return value
#  PRODUCT  

class Product(BaseModel):
    id: UUID

    sku: Annotated[
        str,
        Field(
            min_length=6,
            max_length=36,
            description="Stock Keeping Unit",
            examples=["abc-123", "mobile-456"],
        ),
    ]

    name: Annotated[
        str,
        Field(
            min_length=3,
            max_length=80,
            description="Readable product name (3–80 chars)",
        ),
    ]

    description: Annotated[
        str,
        Field(max_length=80, description="Short product description"),
    ]

    category: Annotated[
        str,
        Field(min_length=3, max_length=50),
    ]

    brand: Annotated[
        str,
        Field(min_length=2, max_length=40),
    ]

    price: Annotated[
        float,
        Field(gt=0, strict=True, description="Base price in INR"),
    ]

    currency: Literal["INR"] = "INR"

    discount_percent: Annotated[
        int,
        Field(ge=0, le=90),
    ] = 0

    stock: Annotated[int, Field(ge=0)]

    is_active: bool

    rating: Annotated[
        float,
        Field(ge=0, le=5, strict=True),
    ]

    tags: Optional[List[str]] = None

    image_url: Annotated[
        Optional[List[AnyUrl]],
        Field(min_length=1),
    ] = None

    seller: Seller
    dimension: DimensionCM
    created_at: datetime

    #  VALIDATORS  #

    @field_validator("sku", mode="after")
    @classmethod
    def validate_sku_format(cls, value: str):
        if "-" not in value:
            raise ValueError("SKU must contain '-'")

        last = value.split("-")[-1]
        if not (len(last) == 3 and last.isdigit()):
            raise ValueError("SKU must end with a 3-digit number like -123")

        return value

    @model_validator(mode="after")
    @classmethod
    def validate_business_rules(cls, model: "Product"):
        if model.stock == 0 and model.is_active:
            raise ValueError("If stock is 0, is_active must be False")

        if model.discount_percent > 0 and model.rating == 0:
            raise ValueError("Discounted product must have a rating")

        return model

    #  COMPUTED FIELD  #

    @computed_field
    @property
    def final_price(self) -> float:
        return round(self.price * (1 - self.discount_percent / 100), 2)

###update pydantic
class DimensionCMUpdate(BaseModel):
    width: Optional[float]=Field(gt=0)
    height: Optional[float]= Field(gt=0)
    length: Optional[float]= Field(gt=0)
    @computed_field
    @property
    def volume_cm3(self) -> float:
        return round(self.length * self.width * self.height, 2)

class SellerUpdate(BaseModel):
    name: Optional[str]=Field(
            min_length=2,
            max_length=80
        ),
    email: Optional[EmailStr]
    website: Optional[AnyUrl]
    
    @field_validator("email", mode="after")
    @classmethod
    def validate_seller_email(cls, value: EmailStr):
        allowed_domains = ["mistore.in", "hpworld.in"]
        domain = str(value).split("@")[-1].lower()

        if domain not in allowed_domains:
            raise ValueError(f"Seller email domain not allowed: {domain}")

        return value

class ProductUpdate(BaseModel):
    name: Optional[str]=Field(
            min_length=3,
            max_length=80,
        ),

    description: Optional[str]=Field(max_length=80)
    
    category: Optional[str]=Field(min_length=3, max_length=50)
    
    brand: Optional[str]=Field(min_length=2, max_length=40)
    
    price: Optional[float]=Field(gt=0)

    currency: Optional[Literal["INR"]]

    discount_percent: Optional[int]=Field(ge=0, le=90)

    stock: Optional[int]= Field(ge=0)
    
    is_active: Optional[bool]

    rating: Optional[float]=Field(ge=0, le=5, strict=True),

    tags: Optional[List[str]] = None

    image_url: Optional[List[AnyUrl]]
    dimension:Optional[DimensionCMUpdate]
    seller:Optional[SellerUpdate]
    

    @model_validator(mode="after")
    @classmethod
    def validate_business_rules(cls, model: "ProductUpdate"):
        # if model.stock is not None and model.is_active is not None:
        if model.stock == 0 and model.is_active:
            raise ValueError("If stock is 0, is_active must be False")

        # if model.discount_percent is not None and model.rating is not None:
        if model.discount_percent > 0 and model.rating == 0:
            raise ValueError("Discounted product must have a rating")

        return model
    #  COMPUTED FIELD  #

    @computed_field
    @property
    def final_price(self) -> Optional[float]:
        if self.price is not None and self.discount_percent is not None:
            return round(self.price * (1 - self.discount_percent / 100), 2)
        return None

