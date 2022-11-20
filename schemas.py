from pydantic import BaseModel
from typing import Optional

class SignUpModel(BaseModel):
    id:Optional[int]
    username:str
    email:str
    password:str
    is_staff:Optional[bool]
    is_active:Optional[bool]


    class  Config:
        orm_mode=True
        schema_extra ={

            'example': {
                "username": "johndoe",
                "email": "johndoe@gmail.com",
                "password": "password",
                "is_staff": False,
                "is_activate": True
            }
        }

class Settings(BaseModel):
    authjwt_secret_key:str = '414c5d69811caafe963a363dddb013b94a71640a5052c97bd513a630c4690115'

class LoginModel(BaseModel):
    username:str
    password:str


class OrderModel(BaseModel):
    id:Optional[int]
    quantity:int
    order_status:Optional[str] = "PENDING"
    pizza_size:Optional[str] = "SMALL"
    user_id:Optional[int]

    class Config:
        orm_model=True
        schema_extra = {
            "example":{
                "quantity":2,
                "pizza_size":"LARGE"

            }
        }
