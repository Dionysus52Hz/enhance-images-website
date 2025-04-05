from fastapi import APIRouter, HTTPException, Body, UploadFile, status, Depends
from src.models.HTTPResponse import ResponseModel, ErrorResponseModel
from src.models.images import ImageSchema, create_image, upload_image
from src.models.enhancers import EnhanceFormSchema
from src.core.skr import skr
from src.core.nni import nni
from src.core.bilinear import bilinear
from src.utils.images import create_upload_file

import os
import io
import numpy as np
import cv2

router = APIRouter(
    prefix="/enhancers",
    tags=["enhancers"],
)


@router.post("/")
async def enhance_image(form_data: EnhanceFormSchema = Depends()):
    try:
        image = await form_data.image.read()
        filename = form_data.image.filename
        basename = os.path.splitext(filename)[0]
        extension = os.path.splitext(filename)[1].lower()

        image = cv2.imdecode(np.frombuffer(image, np.uint8), cv2.IMREAD_COLOR)

        model = form_data.model
        scale_factor = int(form_data.scaleFactor)

        sr = None

        if model == "skr":
            sr = skr(image, scale_factor)
        elif model == "nni":
            sr = nni(image, scale_factor)
        elif model == "bilinear":
            sr = bilinear(image, scale_factor)

        if sr is not None:
            success1, encoded_sr = cv2.imencode(extension, sr)
            success2, encoded_lr = cv2.imencode(extension, image)

            if not success1 or not success2:
                return ErrorResponseModel(
                    code=status.HTTP_400_BAD_REQUEST,
                    message="Something wrong with the image.",
                )

            upload_lr_result = await upload_image(
                create_upload_file(encoded_lr.tobytes(), filename)
            )
            upload_sr_result = await upload_image(
                create_upload_file(encoded_sr.tobytes(), f"{basename}_sr{extension}")
            )

        if upload_lr_result is None or upload_sr_result is None:
            return ErrorResponseModel(
                code=status.HTTP_404_NOT_FOUND,
                message=f"Enhance image failed.",
            )

        return ResponseModel(
            data={
                "lr": upload_lr_result,
                "sr": upload_sr_result,
            },
            code=status.HTTP_200_OK,
            message=f"Enhance image successfully!",
        )

    except HTTPException:
        raise

    except Exception as e:
        return ErrorResponseModel(
            code=status.HTTP_400_BAD_REQUEST,
            message=str(e),
        )
