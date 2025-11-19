FROM pytorch/pytorch:2.9.1-cuda12.8-cudnn9-runtime

ENV PYTHONUNBUFFERED=1 \
    HF_HOME=/app/.cache/huggingface \
    TRANSFORMERS_CACHE=/app/.cache/huggingface \
    HUGGINGFACE_HUB_CACHE=/app/.cache/huggingface

# Можно переопределять при сборке/запуске
ENV BASE_MODEL_ID="stabilityai/stable-diffusion-xl-base-1.0" \
    CONTROLNET_MODEL_ID="diffusers/controlnet-depth-sdxl-1.0" \
    DEPTH_MODEL_ID="Intel/dpt-hybrid-midas"

WORKDIR /app

# torch уже в базовом образе → в requirements.txt его нет
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем код (включая warmup_models.py и app.py)
COPY ./app.py ./
COPY ./warmup_models.py ./
# Предварительно качаем модели (единственный запуск при сборке образа)
RUN python warmup_models.py

# В app.py должен быть что-то вроде:
#   import os, telebot
#   bot = telebot.TeleBot(os.environ["BOT_TOKEN"])
CMD ["python", "app.py"]