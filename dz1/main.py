from model_ad import Ad
from fastapi import FastAPI
from validator import validate_ad

app = FastAPI()

@app.get('/')
async def root():
    return {'message': 'Hello World'}

@app.post('/predict')
async def predict(ad: Ad) -> bool:
    validate_ad(ad)
    if ad.is_verified_seller or ad.images_qty > 0:
        return True
    return False