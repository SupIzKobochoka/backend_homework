from pydantic import BaseModel, StrictInt, StrictStr, StrictBool, Field

class Ad(BaseModel):
    seller_id: StrictInt = Field(ge=0)
    is_verified_seller: StrictBool
    item_id: StrictInt = Field(ge=0)
    name: StrictStr
    description: StrictStr
    category: StrictStr
    images_qty: StrictInt = Field(ge=0)

