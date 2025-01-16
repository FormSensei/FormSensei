from fastapi import FastAPI, UploadFile, File
from PIL import Image
import io

app = FastAPI()

@app.post("/resize/")
async def resize_image(file: UploadFile = File(...), width: int = 100, height: int = 100):
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))
    resized_image = image.resize((width, height))
    img_byte_arr = io.BytesIO()
    resized_image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    return {"filename": file.filename, "content": img_byte_arr}