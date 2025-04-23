from fastapi import APIRouter, HTTPException, Body, UploadFile, status, Depends
from fastapi.responses import StreamingResponse

from src.models.HTTPResponse import ResponseModel, ErrorResponseModel
from src.models.SSEResponse import SSEResponseModel
from src.models.images import ImageSchema, create_image, upload_image

from src.models.enhancers import EnhanceFormSchema
from src.core.skr import skr
from src.core.nni import nni
from src.core.bilinear import bilinear
from src.core.bicubic import bicubic

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

        async def event_generator():

            sr = None
            container = {}
            upload_lr_result = None
            upload_sr_result = None

            if model == "skr":
                for result in skr(image, scale_factor, container):
                    yield result
                sr = container.get("sr")
            elif model == "nni":
                for result in nni(image, scale_factor, container):
                    yield result
                sr = container.get("sr")
            elif model == "bilinear":
                for result in bilinear(image, scale_factor, container):
                    yield result
                sr = container.get("sr")
            elif model == "bicubic":
                for result in bicubic(image, scale_factor, container):
                    yield result
                sr = container.get("sr")

            if sr is not None:
                success1, encoded_sr = cv2.imencode(extension, sr)
                success2, encoded_lr = cv2.imencode(extension, image)

                if not success1 or not success2:
                    yield SSEResponseModel(
                        status="error",
                        message="Something wrong with the image",
                        code=status.HTTP_400_BAD_REQUEST,
                    ).to_sse()
                    return
                    # return ErrorResponseModel(
                    #     code=status.HTTP_400_BAD_REQUEST,
                    #     message="Something wrong with the image.",
                    # )

                # upload_lr_result = await upload_image(
                #     create_upload_file(encoded_lr.tobytes(), filename)
                # )
                # upload_sr_result = await upload_image(
                #     create_upload_file(
                #         encoded_sr.tobytes(), f"{basename}_sr{extension}"
                #     )
                # )
                upload_lr_result = await upload_image(encoded_lr.tobytes())
                upload_sr_result = await upload_image(encoded_sr.tobytes())

            if upload_lr_result is None or upload_sr_result is None:
                yield SSEResponseModel(
                    status="error",
                    code=status.HTTP_404_NOT_FOUND,
                    message="Enhance image failed.",
                ).to_sse()
                return
                # return ErrorResponseModel(
                #     code=status.HTTP_404_NOT_FOUND,
                #     message=f"Enhance image failed.",
                # )

            # return ResponseModel(
            #     data={
            #         "lr": upload_lr_result,
            #         "sr": upload_sr_result,
            #     },
            #     code=status.HTTP_200_OK,
            #     message=f"Enhance image successfully!",
            # )
            yield SSEResponseModel(
                status="completed",
                code=status.HTTP_200_OK,
                message="Enhance image successfully!",
                data={
                    "lr": upload_lr_result,
                    "sr": upload_sr_result,
                },
            ).to_sse()
            return

        return StreamingResponse(event_generator(), media_type="text/event-stream")
    except HTTPException:
        raise

    except Exception as e:
        return ErrorResponseModel(
            code=status.HTTP_400_BAD_REQUEST,
            message=str(e),
        )
