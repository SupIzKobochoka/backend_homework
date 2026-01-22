from fastapi import APIRouter
from model.ad import Ad
from services.ad import check_ad

router = APIRouter()

@router.post('/predict')
async def predict(ad: Ad) -> bool:
    return check_ad(ad=ad)
    