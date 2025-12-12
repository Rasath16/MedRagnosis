from pydantic import BaseModel, Field, field_validator

class SignupRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    
    password: str = Field(..., min_length=6, description="Password must be at least 6 chars")
    
    role: str 

    @field_validator('role')
    @classmethod
    def role_must_be_valid(cls, v: str) -> str:
        if v.lower() not in ['patient', 'doctor']:
            raise ValueError('Role must be either "patient" or "doctor"')
        return v.lower()