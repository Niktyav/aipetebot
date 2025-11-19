import telebot
import os
import logging
from telebot import types
import re
import base64
import torch
from PIL import Image
from diffusers import (
    StableDiffusionXLControlNetImg2ImgPipeline,
    ControlNetModel,
    DPMSolverMultistepScheduler,
)
from transformers import pipeline
from diffusers.utils import load_image
import numpy as np



logging.basicConfig(level=logging.INFO,    
                    format='%(asctime)s - %(levelname)s - %(module)s - %(message)s'
                    )

# Создаем бота
bot = telebot.TeleBot("8211695368:AAFACG4BI1j8PvkKP47g5qTMDoj5KQ6z_sM")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
device = "cuda"
dtype = torch.float16

# === 1. Готовим depth-карту ===
# Можно использовать любую модель depth-estimation, которая выдаёт карту глубины
depth_estimator = pipeline("depth-estimation", model="Intel/dpt-hybrid-midas", device=0)

def make_depth_image(image_path, size=(768, 768)):
    from diffusers.utils import load_image
    import numpy as np

    # Загружаем исходное изображение
    img = load_image(image_path).resize(size)

    # Получаем depth карту (возвращает PIL.Image)
    depth_pil = depth_estimator(img)["depth"]

    # Переводим в NumPy
    depth_np = np.array(depth_pil, dtype=np.float32)

    # Нормализуем 0–255
    depth_np = (depth_np - depth_np.min()) / (depth_np.max() - depth_np.min() + 1e-8)
    depth_np = (depth_np * 255).astype(np.uint8)

    # Делаем 3 канала RGB
    depth_rgb = np.stack([depth_np] * 3, axis=-1)

    return Image.fromarray(depth_rgb)

# === 2. ControlNet ===
controlnet = ControlNetModel.from_pretrained(
    "diffusers/controlnet-depth-sdxl-1.0",
    torch_dtype=dtype,
).to(device)

# === 3. Основной пайплайн (можно поменять на RealVisXL_V4.0 для фотореализма) ===
pipe = StableDiffusionXLControlNetImg2ImgPipeline.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0",
    controlnet=controlnet,
    torch_dtype=dtype,
    variant="fp16",
).to(device)

pipe.scheduler = DPMSolverMultistepScheduler.from_config(
    pipe.scheduler.config,
    use_karras=True,
    algorithm_type="sde-dpmsolver++",
)





# Получение сообщений от юзера
@bot.message_handler(content_types=["text"])
def handle_text(message):
    global understanding_counter
    global payload
    try:
        logging.info("User: ", message.text)
        bot.send_message(message.chat.id, "Ожидается картинка")
    except Exception as e:
        logging.error('Ошибка:',e)
        
        
@bot.message_handler(content_types=['photo'])
def photo(message):       
    fileID = message.photo[-1].file_id   
    file_info = bot.get_file(fileID)
  

    downloaded_file = bot.download_file(file_info.file_path)
    with open("image.jpg", 'wb') as new_file:
        new_file.write(downloaded_file)        
    # === 4. Входное изображение ===
    input_path = "image.jpg"
    init_image = Image.open(input_path).convert("RGB").resize((768, 768))
    depth_image = make_depth_image(input_path, size=(768, 768))

    # === 5. Промпты ===
    prompt = (
        "ultra realistic architectural photo"
    )
    negative_prompt = (
        "3d render, cgi, stylized, cartoon, sketch, painting, lowres, text, watermark, oversaturated"
    )

    # === 6. Генерация ===
    out = pipe(
        prompt=prompt,
        negative_prompt=negative_prompt,
        image=init_image,
        control_image=depth_image,
        strength=0.70,                  # больше = сильнее перерисовка
        guidance_scale=5.0,             # меньше — реалистичнее
        num_inference_steps=40,
        controlnet_conditioning_scale=0.35,  # сила depth
    ).images[0]
        #         photo1 = open('petia.png', 'rb')
    bot.send_photo(message.chat.id, out)  
    out.save("out_depth_base.png")


if __name__ == "__main__":
    # Запускаем бота
    logging.info('Bot starting...')
    bot.polling(none_stop=True, interval=0,timeout= 2000)






