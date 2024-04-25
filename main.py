from fastapi import FastAPI, WebSocket, UploadFile, Form
from fastapi.responses import FileResponse
from fastapi.responses import HTMLResponse
from gradio_client import Client, file
from enum import Enum
import asyncio
from io import BytesIO

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
async def tryon(background: UploadFile = Form(...), garm_img: UploadFile = Form(...), garment_des: str = Form(...), is_checked: bool = True, is_checked_crop: bool = False, denoise_steps: float = 30, seed: float = 42):
    try:
        # Read uploaded files into memory
        background_data = await background.read()
        garm_img_data = await garm_img.read()

        # Call Gradio client predict function
        result = client.predict(
            dict={"background": file(BytesIO(background_data)), "layers": [], "composite": None},
            garm_img=file(BytesIO(garm_img_data)),
            garment_des=garment_des,
            is_checked=is_checked,
            is_checked_crop=is_checked_crop,
            denoise_steps=denoise_steps,
            seed=seed,
            api_name="/tryon"
        )

        # Return the result as a file response
        result_image_data = result[0]
        return FileResponse(BytesIO(result_image_data), media_type='image/png')
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
