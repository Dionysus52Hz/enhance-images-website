from pydantic import BaseModel
from fastapi import UploadFile, File, Form, Depends


class EnhanceFormSchema:
    def __init__(
        self,
        image: UploadFile = File(...),
        model: str = Form(...),
        scaleFactor: int = Form(...),
    ):
        self.image = image
        self.model = model
        self.scaleFactor = scaleFactor
