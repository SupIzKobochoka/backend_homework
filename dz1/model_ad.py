from pydantic import BaseModel
from pydantic import BaseModel, StrictInt, StrictStr, StrictBool

class Ad(BaseModel):
    seller_id: StrictInt
    is_verified_seller: StrictBool
    item_id: StrictInt
    name: StrictStr
    description: StrictStr
    category: StrictStr
    images_qty: StrictInt

