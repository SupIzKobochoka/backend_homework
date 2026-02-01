from pydantic import BaseModel, StrictBool, StrictFloat, Field

class PredictedAd(BaseModel):
    is_violation: StrictBool
    probability: StrictFloat = Field(..., ge=0, le=1)

# class BatchPredictedAd(BaseModel):
#     values: list[PredictedAd] = Field(..., min_length=1, max_length=100) #TODO Подумать, нужно ли min, max и нужна ли здесь эта логика, ведь размер передается через AD