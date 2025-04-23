from fastapi import APIRouter, HTTPException, status, Body, UploadFile
from fastapi.responses import StreamingResponse
from src.models.HTTPResponse import ResponseModel, ErrorResponseModel
from src.models.images import (
    ImageSchema,
    UpdateImageSchema,
    get_images,
    get_image_by_id,
    create_image,
    upload_image,
    update_image,
)
from src.models.SSEResponse import SSEResponseModel

router = APIRouter(
    prefix="/images",
    tags=["images"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def read_images():
    images = await get_images()

    if images is None:
        return ErrorResponseModel(
            code=status.HTTP_404_NOT_FOUND,
            message=f"Cannot retrieve all images",
        )

    return ResponseModel(
        data=images,
        code=status.HTTP_200_OK,
        message="Retrieve images successfully!",
    )


@router.get("/{image_id}")
async def read_image_data(image_id: str):
    try:
        image = await get_image_by_id(image_id)

        if image is None:
            return ErrorResponseModel(
                code=status.HTTP_404_NOT_FOUND,
                message=f"Cannot retrieve image with id {image_id}",
            )

        return ResponseModel(
            data=image,
            code=status.HTTP_200_OK,
            message=f"Retrieve image with id {image_id} successfully!",
        )

    except HTTPException:
        raise

    except Exception as e:
        return ErrorResponseModel(
            code=status.HTTP_400_BAD_REQUEST,
            message=str(e),
        )


@router.post("/")
async def add_image(image: ImageSchema = Body(...)):
    try:

        image = image.model_dump(by_alias=True, exclude=["id"])

        new_image = await create_image(image)

        if new_image is None:
            return ErrorResponseModel(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Cannot add new image.",
            )

        return ResponseModel(
            data=new_image,
            code=status.HTTP_200_OK,
            message="Image add successfully.",
        )

    except Exception as e:
        return ErrorResponseModel(
            code=status.HTTP_400_BAD_REQUEST,
            message=str(e),
        )


@router.post("/upload")
async def upload_image_to_cloud(image: UploadFile):
    try:
        content = await image.read()

        async def event_generator():
            yield SSEResponseModel(
                status="processing",
                message="Uploading image",
                code=status.HTTP_200_OK,
            ).to_sse()

            upload_result = await upload_image(content)

            if upload_result is None:
                yield SSEResponseModel(
                    status="error",
                    message="Upload image failed",
                    code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                ).to_sse()
                return

            yield SSEResponseModel(
                status="completed",
                message="Upload completed",
                code=status.HTTP_200_OK,
                data=upload_result,
            ).to_sse()
            return

        return StreamingResponse(event_generator(), media_type="text/event-stream")

    except Exception as e:
        return ErrorResponseModel(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=str(e),
        )


@router.put("/{image_id}")
async def update_image_data(image_id: str, image: UpdateImageSchema = Body(...)):
    try:
        image = {
            k: v for k, v in image.model_dump(by_alias=True).items() if v is not None
        }

        update_result = await update_image(image_id, image)

        if update_result is None:
            return ErrorResponseModel(
                code=status.HTTP_404_NOT_FOUND,
                message=f"Cannot update image with id {image_id}",
            )

        return ResponseModel(
            data=update_result,
            code=status.HTTP_200_OK,
            message=f"Update image with id {image_id} successfully!",
        )

    except HTTPException:
        raise

    except Exception as e:
        return ErrorResponseModel(
            code=status.HTTP_400_BAD_REQUEST,
            message=str(e),
        )
