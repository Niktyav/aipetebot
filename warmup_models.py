# warmup_models.py
import os
import torch
from diffusers import StableDiffusionXLControlNetImg2ImgPipeline, ControlNetModel
from transformers import pipeline
from PIL import Image

BASE_MODEL_ID = os.getenv("BASE_MODEL_ID", "stabilityai/stable-diffusion-xl-base-1.0")
CONTROLNET_MODEL_ID = os.getenv("CONTROLNET_MODEL_ID", "diffusers/controlnet-depth-sdxl-1.0")
DEPTH_MODEL_ID = os.getenv("DEPTH_MODEL_ID", "Intel/dpt-hybrid-midas")

print(f"Downloading SDXL base model (fp16): {BASE_MODEL_ID}")
print(f"Downloading ControlNet model (fp16): {CONTROLNET_MODEL_ID}")
print(f"Downloading depth model: {DEPTH_MODEL_ID}")

# 1. SDXL + ControlNet — строго так же, как в app.py (fp16 + safetensors + variant="fp16")
controlnet = ControlNetModel.from_pretrained(
    CONTROLNET_MODEL_ID,
    torch_dtype=torch.float16,
    use_safetensors=True,
    variant="fp16",
)

pipe = StableDiffusionXLControlNetImg2ImgPipeline.from_pretrained(
    BASE_MODEL_ID,
    controlnet=controlnet,
    torch_dtype=torch.float16,
    use_safetensors=True,
    variant="fp16",
)

# 2. depth-estimation
depth_pipe = pipeline("depth-estimation", model=DEPTH_MODEL_ID)

# Лёгкий прогрев, чтобы докачались мелкие файлы, если нужно
dummy = Image.new("RGB", (64, 64), "white")
_ = depth_pipe(dummy)

print("All models (fp16 + depth) downloaded to HuggingFace cache.")
