from fastapi import FastAPI, WebSocket, File, UploadFile, Form
from fastapi.responses import FileResponse
from fastapi.responses import HTMLResponse
from gradio_client import Client, file
from enum import Enum
import asyncio

# Define a custom enum for job status
class JobStatus(str, Enum):
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

app = FastAPI()
client = Client("yisol/IDM-VTON")

# Store WebSocket connections
connections = set()

# WebSocket route to handle job status updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connections.add(websocket)
    try:
        while True:
            await asyncio.sleep(1)  # Update status every second (for demonstration purposes)
            # Retrieve job status
            # You need to implement a way to track the job status in your application
            status = get_job_status()
            await websocket.send_text(status.value)
    finally:
        connections.remove(websocket)

# Sample function to simulate job status
def get_job_status():
    # You need to implement logic to retrieve the actual job status
    # For demonstration purposes, let's return a hardcoded status
    return JobStatus.STARTING

# Route to initiate the try-on process
@app.post("/tryon")
async def tryon(background: UploadFile = File(...), garm_img: UploadFile = File(...), garment_des: str = Form(...), is_checked: bool = True, is_checked_crop: bool = False, denoise_steps: float = 30, seed: float = 42):
    # Save uploaded files
    background_path = f"static/{background.filename}"
    garm_img_path = f"static/{garm_img.filename}"

    with open(background_path, "wb") as bg_file, open(garm_img_path, "wb") as garm_file:
        bg_file.write(await background.read())
        garm_file.write(await garm_img.read())

    # Update job status to RUNNING
    # You need to implement a way to track the job status in your application
    # For demonstration purposes, let's assume the job is always RUNNING
    update_job_status(JobStatus.RUNNING)

    try:
        # Call Gradio client predict function
        result = client.predict(
            dict={"background": file(background_path), "layers": [], "composite": None},
            garm_img=file(garm_img_path),
            garment_des=garment_des,
            is_checked=is_checked,
            is_checked_crop=is_checked_crop,
            denoise_steps=denoise_steps,
            seed=seed,
            api_name="/tryon"
        )

        # Update job status to SUCCESS
        # You need to implement a way to track the job status in your application
        # For demonstration purposes, let's assume the job always succeeds
        update_job_status(JobStatus.SUCCESS)
        
        # Return the result as a file response
        result_image_path = result[0]
        return FileResponse(result_image_path, media_type='image/png')
    except Exception as e:
        # Update job status to FAILED if an error occurs
        # You need to implement error handling and update the status accordingly
        update_job_status(JobStatus.FAILED)
        raise e

# Sample function to update job status
def update_job_status(status: JobStatus):
    # You need to implement logic to update the job status in your application
    # For demonstration purposes, let's print the status
    print("Job status:", status)

# Frontend can connect to the WebSocket endpoint to receive real-time updates on the job status
