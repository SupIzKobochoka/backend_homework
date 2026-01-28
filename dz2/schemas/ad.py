from pydantic import BaseModel, StrictInt, StrictStr, StrictBool, Field

class Ad(BaseModel):
    seller_id: StrictInt = Field(ge=0)
    is_verified_seller: StrictBool
    item_id: StrictInt = Field(ge=0)
    name: StrictStr
    description: StrictStr
    category: StrictInt
    images_qty: StrictInt = Field(ge=0, le=10)

# class BatchAd(BaseModel):
#     ads: list[Ad] = Field(..., min_length=1, max_length=100) #TODO Подумать, нужно ли min, max