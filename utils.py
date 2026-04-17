import base64
from io import BytesIO
from PIL import Image

def base64_to_pil(base64_str: str) -> Image.Image:
    """Convertit une chaîne base64 en image PIL."""
    if "," in base64_str:
        base64_str = base64_str.split(",", 1)[1]
    image_data = base64.b64decode(base64_str)
    return Image.open(BytesIO(image_data)).convert("RGB")

def pil_to_base64(image: Image.Image) -> str:
    """Convertit une image PIL en chaîne base64 (format PNG)."""
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{img_str}"

def preprocess_image(image: Image.Image, width: int, height: int) -> Image.Image:
    """Redimensionne l'image pour qu'elle soit compatible avec l'IA (multiples de 8)."""
    width = (width // 8) * 8
    height = (height // 8) * 8
    return image.resize((width, height), Image.Resampling.LANCZOS)
