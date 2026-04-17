import cv2
import numpy as np
from PIL import Image
from rembg import remove

class ImageProcessor:
    @staticmethod
    def remove_background(image: Image.Image) -> Image.Image:
        """
        Supprime l'arrière-plan de l'image pour isoler le produit.
        Utilise la bibliothèque rembg.
        """
        try:
            # rembg supprime le fond et retourne une image avec transparence (RGBA)
            result_rgba = remove(image)
            
            # Pour SDXL / ControlNet on convertit souvent sur fond blanc pour de meilleurs résultats
            background = Image.new("RGBA", result_rgba.size, (255, 255, 255, 255))
            composite = Image.alpha_composite(background, result_rgba)
            
            # Retourner en RGB 
            return composite.convert("RGB")
        except Exception as e:
            print(f"Erreur lors de la suppression de l'arrière-plan : {e}")
            return image.convert("RGB")

    @staticmethod
    def generate_canny(image: Image.Image, low_threshold: int = 100, high_threshold: int = 200) -> Image.Image:
        """
        Génère une carte de contours (Canny Edge) qui servira de guide au ControlNet.
        Cela permet à l'IA de conserver les formes exactes du produit.
        """
        try:
            # Convertir l'image PIL en un tableau exploitable par OpenCV
            image_np = np.array(image.convert("RGB"))
            
            # Extraire les contours
            canny_edges = cv2.Canny(image_np, low_threshold, high_threshold)
            
            # Le format attendu par ControlNet (diffusers) est une image RGB (bien que visuellement N&B)
            # avec la forme shape = (H, W, 3)
            canny_rgb = cv2.cvtColor(canny_edges, cv2.COLOR_GRAY2RGB)
            
            return Image.fromarray(canny_rgb)
        except Exception as e:
            print(f"Erreur lors de l'extraction de la carte de contours Canny : {e}")
            # En cas d'échec on renvoie une image "vierge" ou l'image originale
            return image

