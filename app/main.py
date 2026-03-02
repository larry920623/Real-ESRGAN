import os
import shutil
import subprocess
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_DIR = os.path.join(BASE_DIR, "inputs")
RESULTS_DIR = os.path.join(BASE_DIR, "results")

os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)


@app.get("/")
def read_root():
    return {"message": "Real-ESRGAN API is running!"}


@app.post("/upload")
async def process_image(file: UploadFile = File(...)):
    filename = file.filename
    input_path = os.path.join(INPUT_DIR, filename)
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    cmd = [
        "python", "inference_realesrgan.py",
        "-n", "RealESRGAN_x4plus",
        "-i", input_path,
        "-o", RESULTS_DIR,
        "--fp32",
        "--tile", "400"
    ]
    print(f"正在執行: {' '.join(cmd)}")

    try:
        subprocess.run(cmd, check=True, cwd=BASE_DIR)
    except subprocess.CalledProcessError as e:
        return {"error": "模型執行失敗", "detail": str(e)}

    name, ext = os.path.splitext(filename)
    output_filename = f"{name}_out{ext}"
    output_path = os.path.join(RESULTS_DIR, output_filename)

    if os.path.exists(output_path):
        return FileResponse(output_path)
    else:
        return {"error": "找不到輸出檔案", "path": output_path}
