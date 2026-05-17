import os
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import nest_asyncio
from pyngrok import ngrok

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

# Create the folder if it doesn't exist (this works when running in Colab)
os.makedirs(DRIVE_OUTPUT_DIR, exist_ok=True)

# Mount the static directory so frontend can fetch images
app.mount("/outputs", StaticFiles(directory=DRIVE_OUTPUT_DIR), name="outputs")


@app.get("/")
def read_root():
    return {"message": "DocOS Backend is running successfully!"}


@app.post("/process-pdf")
async def process_pdf(file: UploadFile = File(...)):
    """
    Placeholder endpoint for Phase 1. 
    We will add Qwen3-VL and Layout Detection here later.
    """
    # 1. Read PDF
    content = await file.read()
    
    # Placeholder: We pretend we processed it and cropped an image
    # For now, just returning a fake Scene Graph JSON
    fake_scene_graph = {
        "page": 1,
        "filename": file.filename,
        "elements": [
            {
                "id": "txt_1",
                "type": "text",
                "content": "This is where AI extracted text will go.",
                "bbox": [10, 10, 200, 50],
                "editable": True
            }
        ]
    }
    
    return {"status": "success", "scene_graph": fake_scene_graph}


if __name__ == "__main__":
    # This block is specifically to run FastAPI inside Google Colab using ngrok
    port = 8000
    
    # Setup Ngrok (User will need to set their auth token in Colab later)
    # ngrok.set_auth_token("YOUR_NGROK_TOKEN") 
    public_url = ngrok.connect(port).public_url
    print(f"\\n\\n>>> API is available at: {public_url} <<<\\n\\n")
    
    nest_asyncio.apply()
    uvicorn.run(app, host="0.0.0.0", port=port)
