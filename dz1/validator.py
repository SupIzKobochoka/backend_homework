from model_ad import Ad
from fastapi import HTTPException

def validate_ad(ad: Ad) -> None:
    checkers = {'seller_id': [lambda x: x < 0, 'seller_id < 0'],
                'item_id': [lambda x: x < 0, 'item_id < 0'],
                'images_qty': [lambda x: x < 0, 'images_qty < 0']
                }
    
    for field, (check_func, message) in checkers.items():
        if check_func(getattr(ad, field)):
            raise HTTPException(status_code=400, detail=message)
        

    