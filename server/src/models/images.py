from fastapi import UploadFile
from pydantic import BaseModel, ConfigDict, Field
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated
from bson import ObjectId
from pymongo import ReturnDocument
from .database import get_collection
from motor.motor_asyncio import (
    AsyncIOMotorCollection,
)
from typing import Optional
from config import settings


import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url

cloudinary.config(
    cloud_name=settings.CLOUDINARY_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True,
)


PyObjectId = Annotated[str, BeforeValidator(str)]

_images_collection: Optional[AsyncIOMotorCollection] = None


class ImageSchema(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    cloudinaryURL: str = Field(...)
    height: Optional[int] = Field(default=None)
    lrID: Optional[PyObjectId] = Field(default=None)
    name: str = Field(...)
    model: Optional[str] = Field(default=None)
    scaleFactor: Optional[int] = Field(default=1)
    size: Optional[int] = Field(default=None)
    width: Optional[int] = Field(default=None)


class ImageCollection(BaseModel):
    images: list[ImageSchema]


class UpdateImageSchema(BaseModel):
    cloudinaryURL: Optional[str] = None
    height: Optional[int] = None
    lrID: Optional[PyObjectId] = None
    name: Optional[str] = None
    model: Optional[str] = None
    scaleFactor: Optional[int] = None
    size: Optional[int] = None
    width: Optional[int] = None


async def create_image(image: dict):
    global _images_collection
    try:
        if _images_collection is None:
            _images_collection = get_collection("images")

        new_image = await _images_collection.insert_one(image)
        print(new_image)

        if not new_image:
            return None

        created_image = await _images_collection.find_one(
            {"_id": new_image.inserted_id}
        )

        return ImageSchema(**created_image)
    except Exception as e:
        print(e)


async def get_images():
    global _images_collection

    _images_collection = get_collection("images")
    images = await _images_collection.find().to_list()

    if not images:
        return None

    return ImageCollection(images=images)


async def get_image_by_id(id: str):
    global _images_collection
    try:
        if _images_collection is None:
            _images_collection = get_collection("images")

        image = await _images_collection.find_one({"_id": ObjectId(id)})
        if not image:
            return None

        return ImageSchema(**image)
    except Exception as e:
        print(e)


async def upload_image(image: UploadFile):
    try:
        upload_result = cloudinary.uploader.upload(image.file)

        if not upload_result:
            return None

        file_url = upload_result["secure_url"]
        return {"url": file_url}
    except Exception as e:
        print(e)


async def update_image(image_id: str, image: dict):
    global _images_collection
    try:
        if _images_collection is None:
            _images_collection = get_collection("images")

        if len(image) >= 1:
            update_result = await _images_collection.find_one_and_update(
                {"_id": ObjectId(image_id)},
                {"$set": image},
                return_document=ReturnDocument.AFTER,
            )

            if update_result is not None:
                return ImageSchema(**update_result)
            else:
                return None

        if (
            existing_image := await _images_collection.find_one(
                {"_id": ObjectId(image_id)}
            )
        ) is not None:
            return ImageSchema(**existing_image)

    except Exception as e:
        print(e)
