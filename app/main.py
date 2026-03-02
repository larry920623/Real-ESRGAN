import os
import shutil
import subprocess
import uuid
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from app.worker import process_image_task
from celery.result import AsyncResult
from app.worker import celery_app

app = FastAPI()

SHARED_DIR = "/data"
INPUT_DIR = os.path.join(SHARED_DIR, "inputs")
RESULTS_DIR = os.path.join(SHARED_DIR, "results")

os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)


# @app.get("/")
# def read_root():
#     return {"message": "Real-ESRGAN API is running!"}


@app.post("/upload")
async def process_image(file: UploadFile = File(...)):
# 1. 存檔 (跟之前一樣，但存到共享區)
    file_ext = os.path.splitext(file.filename)[1]
    safe_filename = f"{uuid.uuid4()}{file_ext}"
    input_path = os.path.join(INPUT_DIR, safe_filename)
    
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 預測輸出檔名 (Real-ESRGAN 慣例)
    output_filename = f"{safe_filename.split('.')[0]}_out{file_ext}"
    output_path = os.path.join(RESULTS_DIR, output_filename)

    # 2. 【關鍵改變】: 不直接跑，而是丟給 Celery (delay)
    # 這裡會瞬間回傳一個 task，不會卡住
    task = process_image_task.delay(input_path, output_path, "400")

    # 3. 馬上回傳號碼牌 (Task ID)
    return {"task_id": task.id, "status": "processing"}

@app.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """查詢任務狀態的 API"""
    task_result = AsyncResult(task_id, app=celery_app)

    if task_result.state == 'PENDING':
        return {"status": "pending", "message": "排隊中或正在處理..."}
    
    elif task_result.state == 'SUCCESS':
        # 任務完成，回傳結果資訊
        result_data = task_result.result
        if result_data.get("status") == "completed":
             # 這裡可以回傳圖片下載連結
             return {"status": "success", "download_url": f"/download/{os.path.basename(result_data['output_path'])}"}
        else:
             return {"status": "failed", "error": result_data.get("error")}

    elif task_result.state == 'FAILURE':
        return {"status": "failed", "error": str(task_result.result)}

    return {"status": task_result.state}

# 新增一個下載圖片的端點
@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(RESULTS_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "File not found"}