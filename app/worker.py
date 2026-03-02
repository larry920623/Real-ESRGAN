import os
import subprocess
from celery import Celery

celery_app = Celery(
    "worker",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0"
)

@celery_app.task(name="process_image_task")
def process_image_task(input_path: str, output_path: str, tile_size: str):
    """
    這個函式會被 Celery Worker 在背景執行，不會卡住 API。
    """
    
    cmd = [
        "python", "inference_realesrgan.py",
        "-n", "RealESRGAN_x4plus",
        "-i", input_path,
        "-o", os.path.dirname(output_path), # Real-ESRGAN 的 -o 是指定資料夾
        "--fp32",
        "--tile", tile_size
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        return {"status": "failed", "error": result.stderr}

    return {"status": "completed", "output_path": output_path}