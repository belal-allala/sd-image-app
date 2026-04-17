import torch
from typing import List, Callable, Optional
from PIL import Image

from .model_loader import ModelLoader
from .processor import ImageProcessor
from utils.image_utils import resize_image_by_ratio

class AdGenerator:
    def __init__(self):
        """
        Initialise le générateur de publicité en s'assurant de récupérer la 
        pipeline chargée depuis le ModelLoader (qui est un Singleton).
        """
        try:
            self.model_loader = ModelLoader()
            self.pipeline = self.model_loader.get_pipeline()
        except Exception as e:
            print(f"Erreur lors de l'initialisation du AdGenerator : {e}")
            self.pipeline = None

    def generate(
        self,
        prompt: str,
        list_of_images: List[Image.Image],
        format_choice: str,
        quality_level: str = "high",
        callback: Optional[Callable[[int, int, float], None]] = None
    ) -> Optional[Image.Image]:
        """
        Génère une image publicitaire SDXL à partir de photos de produits.

        Args:
            prompt: Description textuelle (ex: "Bouteille de parfum sur la plage de sable fin, lumière dorée...").
            list_of_images: 1 à 9 photos du produit (pour l'IP-Adapter).
            format_choice: 'post', 'story' ou 'paysage'.
            quality_level: 'fast' (ex: SDXL Lightning) = 4 étapes, 'high' = 8+ étapes.
            callback: Fonction appelée à chaque étape (step) pour envoyer la progression via WebSocket.
                      Doit accepter (step, total_steps, progress_percentage).
        """
        if self.pipeline is None:
            print("Erreur: Impossible de générer, la pipeline IA n'est pas disponible.")
            return None

        if not list_of_images or len(list_of_images) == 0:
            print("Erreur: Au moins une photo de produit est nécessaire.")
            return None

        # Limite de 9 images pour l'identificateur de produit
        if len(list_of_images) > 9:
            list_of_images = list_of_images[:9]
            print("Attention : Nombre d'images limité au maximum de 9.")

        try:
            # --- PREPARATION --- #
            # L'image structurelle de base est la première image de la liste
            main_product_img = list_of_images[0]
            
            # 1. Détourage du produit (suppression du fond via rembg)
            isolated_product = ImageProcessor.remove_background(main_product_img)
            
            # 2. Redimensionnement (Resize et Cropping) selon le format cible 
            # Les formats sont gérés intelligemment dans image_utils.py et 
            # ajustent l'image selon des multiples de 8.
            sized_product = resize_image_by_ratio(isolated_product, format_choice)
            
            # 3. Génération de la carte Canny pour ControlNet
            # Cette carte force le générateur à respecter rigoureusement la forme du produit.
            canny_map = ImageProcessor.generate_canny(sized_product)

            # --- SETUP DE GENERATION --- #
            # Définir l'influence de l'IP Adapter (0.8 est généralement un bon équilibre 
            # pour conserver l'identité sans sacrifier le prompt)
            self.pipeline.set_ip_adapter_scale(0.8)

            # Nombre d'étapes (Le SDXL Base requiert beaucoup d'étapes pour retirer le bruit)
            # En V4 avec SDXL Base : 30 étapes = Fast / Standard, 45 étapes = High / Pro
            total_steps = 30 if quality_level == "fast" else 45

            # --- GESTION DU CALLBACK (POUR WEBSOCKET) --- #
            def step_callback(pipeline_ref, step_index: int, timestep: int, callback_kwargs: dict):
                """Wrapper du callback compatible avec la version récente de diffusers."""
                if callback:
                    # step_index commence à 0, donc +1
                    current_step = step_index + 1
                    # Calcul naïf du pourcentage selon nos itérations
                    progress_pct = (current_step / total_steps) * 100
                    
                    # On appelle la fonction de rappel fournie par l'appelant
                    # (ex: la route WebSocket dans main.py)
                    callback(current_step, total_steps, progress_pct)
                return callback_kwargs

            # Options avancées de guidance (Guidance scale plus faible recommandé pour Lightning)
            guidance_scale = 1.5 if quality_level == "fast" else 3.5

            # Lancement natif du moteur
            print(f"Lancement de la génération : format {format_choice}, {total_steps} étapes.")
            
            outputs = self.pipeline(
                prompt=prompt,
                image=canny_map,                  # Image pour piloter le ControlNet
                ip_adapter_image=list_of_images,  # Liste des images pour piloter l'identité (IP-Adapter)
                num_inference_steps=total_steps,
                controlnet_conditioning_scale=0.75, # Force de la forme Canny
                guidance_scale=guidance_scale,
                width=sized_product.width,
                height=sized_product.height,
                callback_on_step_end=step_callback    # Envoi de la progression step-by-step
            )

            # La génération renvoie un tableau d'images, on récupère la première
            final_ad_image = outputs.images[0]
            print("Génération réussie.")
            return final_ad_image

        except torch.cuda.OutOfMemoryError as e:
            # Capture de l'erreur VRAM pour éviter le crash serveur
            print(f"Erreur VRAM: Out of Memory. Trop de ressources demandées. : {e}")
            torch.cuda.empty_cache()
            return None
        except Exception as e:
            print(f"Erreur fatale lors de la génération publicitaire : {e}")
            return None

