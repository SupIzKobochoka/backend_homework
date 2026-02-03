from fastapi import APIRouter, Request, Depends, HTTPException
from schemas.ad import Ad
from schemas.predicted import PredictedAd
from model import get_pred
from typing import Callable
from client.postgres import get_pg_connection
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter()

def get_model(request: Request) -> Callable:
    try:
        return request.app.state.model
    except AttributeError:
        logger.exception('model doesnt found')
        raise HTTPException(503, detail='Service Unavailable')

async def get_ad(ad_id: int
                 ) -> dict:
    query = '''
        --sql 
        SELECT *
        FROM public.ads
        INNER JOIN public.sellers
            ON public.sellers.seller_id = public.ads.seller_id
        WHERE public.ads.ad_id = $1
        ;
        '''
    async with get_pg_connection() as connection:  
        ad = await connection.fetchrow(query, ad_id)
    return ad
    
def get_ad_provider():
    return get_ad

@router.post('/predict_one')
def predict_one(ad: Ad, 
                model = Depends(get_model)
                ) -> PredictedAd:
    logger.info(f'data input: {ad.model_dump()}')
    try:
        predicted = get_pred(model=model, ad=ad.model_dump())
        logger.info(f'predicted: {predicted}')
        return PredictedAd(**predicted)
    except Exception as eget: 
        logger.exception(f'error while prediction, {e}')
        raise HTTPException(500, detail=f'Internal Server Error while prediction')

@router.post('/simple_predict')
async def simple_predict(ad_id: int, 
                         model = Depends(get_model),
                         get_ad = Depends(get_ad_provider)
                         ) -> PredictedAd:
    try:
        ad = await get_ad(ad_id)
    except Exception as e:
        logger.exception(f'error while data base query, {e}')
        raise HTTPException(500, detail=f'Internal Server Error while data base query')
    if ad is None:
        logger.exception(f'No such ad_id: {ad_id}')
        raise HTTPException(404, detail=f'No such ad_id: {ad_id}')
    ad = dict(ad)
    logger.info(f'data input: {ad}')
    try:
        predicted = get_pred(model=model, ad=ad)
        logger.info(f'predicted: {predicted}')
        return PredictedAd(**predicted)
    except Exception as e: 
        logger.exception(f'error while prediction, {e}')
        raise HTTPException(500, detail=f'Internal Server Error while prediction')
