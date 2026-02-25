# 1. 選擇基底映像檔 (Base Image)
# 選用包含 CUDA 12.1 和 PyTorch 2.1 的開發版 (devel)，這樣才有 nvcc 編譯器
FROM pytorch/pytorch:2.1.2-cuda12.1-cudnn8-devel

# 2. 設定環境變數 (避免安裝時跳出互動視窗)
ENV DEBIAN_FRONTEND=noninteractive

# 3. 安裝系統層級依賴 (OpenCV 必須要有 libgl1 才能跑)
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# 4. 設定工作目錄
WORKDIR /app

# 5. 複製 requirements.txt 並安裝 Python 依賴
# 先只複製這個檔案，利用 Docker Cache 機制加速建置
COPY requirements.txt .

# 升級 pip 並安裝依賴
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install fastapi "uvicorn[standard]" python-multipart

# 6. 🔥 關鍵技術亮點：自動修正 BasicSR 的 Bug 🔥
# 面試時可以說：我用 sed 指令在建置過程中自動修復了依賴庫的版本衝突，不需要手動介入。
# 注意：這個路徑是針對 pytorch/pytorch 基底映像檔的標準路徑 (Python 3.10)
RUN sed -i 's/from torchvision.transforms.functional_tensor import rgb_to_grayscale/from torchvision.transforms.functional import rgb_to_grayscale/g' \
    /opt/conda/lib/python3.10/site-packages/basicsr/data/degradations.py

# 7. 複製專案的所有程式碼
COPY . .

# 8. 編譯 Real-ESRGAN (需要 CUDA 環境)
RUN python setup.py develop

# 9. 下載模型權重
# 把模型直接燒進 Image 裡，這樣容器啟動就能用，不用掛載
RUN mkdir -p weights && \
    wget https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth -P weights/

# 10. 設定容器啟動時的指令
# 注意：這裡加上 --host 0.0.0.0 才能讓外部存取
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]