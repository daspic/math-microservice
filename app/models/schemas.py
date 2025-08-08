from pydantic import BaseModel, Field


class FactorialRequest(BaseModel):
    number: int = Field(..., ge=0, description="Must be a positive integer")


class FibonacciRequest(BaseModel):
    n: int = Field(..., ge=0, description="Must be a positive integer")


class PowerRequest(BaseModel):
    base: float
    exponent: float


class OperationRecord(BaseModel):
    id: int
    operation: str
    input_data: str
    result: float

    model_config = {
        "from_attributes": True
    }
