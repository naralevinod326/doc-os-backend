import os
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import nest_asyncio
from pyngrok import ngrok
from pdf2image import convert_from_bytes
import uuid

app = FastAPI(title="DocOS Backend Engine")

# CORS setup to allow your local frontend to talk to this Colab API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development, allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Google Drive path where we will save images (Colab environment)
DRIVE_OUTPUT_DIR = "/content/drive/MyDrive/DocOS_Outputs"
os.makedirs(DRIVE_OUTPUT_DIR, exist_ok=True)
app.mount("/outputs", StaticFiles(directory=DRIVE_OUTPUT_DIR), name="outputs")

@app.get("/")
def read_root():
    return {"message": "DocOS Backend is running successfully!"}

@app.post("/process-pdf")
async def process_pdf(file: UploadFile = File(...)):
    """
    Step 2: PDF Rasterization & Basic Image saving.
    We convert the PDF to an image and save it to Google Drive.
    """
    print(f"Receiving file: {file.filename}")
    content = await file.read()
    
    # 1. Convert first page of PDF to Image (Rasterization)
    images = convert_from_bytes(content, first_page=1, last_page=1)
    page_image = images[0]
    
    # 2. Save the image to Google Drive
    image_id = str(uuid.uuid4())[:8]
    image_filename = f"page_1_{image_id}.png"
    image_path = os.path.join(DRIVE_OUTPUT_DIR, image_filename)
    page_image.save(image_path, "PNG")
    
    # URL to access this image via our FastAPI server
    image_url = f"/outputs/{image_filename}"
    
    # 3. Create a dynamic Scene Graph
    scene_graph = {
        "page": 1,
        "filename": file.filename,
        "width": page_image.width,
        "height": page_image.height,
        "elements": [
            {
                "id": f"bg_{image_id}",
                "type": "background_image",
                "src_url": image_url,
                "bbox": [0, 0, page_image.width, page_image.height],
                "editable": False
            },
            {
                "id": "txt_example",
                "type": "text",
                "content": "AI text extraction will replace this soon!",
                "bbox": [100, 100, 400, 200],
                "editable": True
            }
        ]
    }
    
    return {"status": "success", "scene_graph": scene_graph}


if __name__ == "__main__":
    # This block is specifically to run FastAPI inside Google Colab using ngrok
    port = 8000
    
    # Setup Ngrok (User will need to set their auth token in Colab later)
    # ngrok.set_auth_token("YOUR_NGROK_TOKEN") 
    public_url = ngrok.connect(port).public_url
    print(f"\\n\\n>>> API is available at: {public_url} <<<\\n\\n")
    
    nest_asyncio.apply()
    uvicorn.run(app, host="0.0.0.0", port=port)
