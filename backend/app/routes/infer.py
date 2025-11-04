"""One-off inference routes."""
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import cv2
import numpy as np
from io import BytesIO

from app.config import settings

router = APIRouter()


@router.post("")
async def infer_image(file: UploadFile = File(...)):
    """Run inference on a single image."""
    # Read image
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if image is None:
        raise HTTPException(status_code=400, detail="Invalid image format")
    
    # TODO: Integrate with orchestrator pipeline
    # For now, return placeholder
    return JSONResponse({
        "count": 0,
        "boxes": [],
        "heatmap": None,
        "model": "placeholder",
    })

