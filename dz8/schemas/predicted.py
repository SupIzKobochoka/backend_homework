from pydantic import BaseModel, StrictBool, StrictFloat, Field

class PredictedAd(BaseModel):
    is_violation: StrictBool
    probability: StrictFloat = Field(..., ge=0, le=1)