from pydantic import BaseModel
from fastapi import UploadFile, File, Form, Depends


class EnhanceFormSchema(BaseModel):
    image: UploadFile = File(...)
    model: str = Form(...)
    scaleFactor: int = Form(...)
