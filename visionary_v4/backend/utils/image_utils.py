import base64
from io import BytesIO
from PIL import Image

def base64_to_pil(base64_str: str) -> Image.Image:
    """Convertit une chaîne Base64 en un objet Image PIL."""
    if "," in base64_str:
        base64_str = base64_str.split(",", 1)[1]
    image_data = base64.b64decode(base64_str)
    return Image.open(BytesIO(image_data)).convert("RGB")

def pil_to_base64(image: Image.Image, format="PNG") -> str:
    """Convertit un objet Image PIL en chaîne Base64."""
    buffered = BytesIO()
    image.save(buffered, format=format)
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/{format.lower()};base64,{img_str}"

def resize_image_by_ratio(image: Image.Image, ratio_name: str) -> Image.Image:
    """
    Redimensionne intelligemment l'image selon un ratio.
    ratio_name: 'post' (1:1), 'story' (9:16), 'paysage' (16:9)
    """
    width, height = image.size
    
    # Définition des ratios cibles (width / height)
    ratios = {
        'post': 1.0,         # 1:1
        'story': 9.0 / 16.0, # 9:16
        'paysage': 16.0 / 9.0 # 16:9
    }
    
    target_ratio = ratios.get(ratio_name.lower(), 1.0)
    current_ratio = width / height
    
    # Crop to ratio
    if current_ratio > target_ratio:
        # L'image est trop large, on coupe sur les côtés
        new_width = int(target_ratio * height)
        offset = (width - new_width) // 2
        crop_box = (offset, 0, width - offset, height)
    else:
        # L'image est trop haute, on coupe en haut et en bas
        new_height = int(width / target_ratio)
        offset = (height - new_height) // 2
        crop_box = (0, offset, width, height - offset)
        
    cropped_img = image.crop(crop_box)
    
    # Assurer que les dimensions sont des multiples de 8 pour Stable Diffusion
    final_width = (cropped_img.width // 8) * 8
    final_height = (cropped_img.height // 8) * 8
    
    return cropped_img.resize((final_width, final_height), Image.Resampling.LANCZOS)
