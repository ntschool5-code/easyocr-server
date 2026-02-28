# Use slim Python image
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for OpenCV/EasyOCR
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install CPU-only PyTorch FIRST (much smaller than full PyTorch with CUDA)
RUN pip install --no-cache-dir \
    torch==2.2.0+cpu \
    torchvision==0.17.0+cpu \
    --index-url https://download.pytorch.org/whl/cpu

# Install EasyOCR and other dependencies
RUN pip install --no-cache-dir \
    easyocr==1.7.1 \
    flask==3.0.3 \
    Pillow==10.3.0 \
    numpy==1.26.4

# Copy app code
COPY . .

# Pre-download EasyOCR models at build time (avoids cold start delay)
RUN python -c "import easyocr; easyocr.Reader(['en', 'hi'], gpu=False)" || true

EXPOSE 5001

CMD ["python", "app.py"]
