import torch
from diffusers import StableDiffusionPipeline, StableDiffusionImg2ImgPipeline
from typing import Optional, Callable
from PIL import Image

class ImageEngine:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ImageEngine, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_id = "runwayml/stable-diffusion-v1-5"
        
        print(f"Chargement du modèle sur {self.device}...")
        
        # Optimize memory using float16 for CUDA
        torch_dtype = torch.float16 if self.device == "cuda" else torch.float32

        # 1. Base pipeline: Txt2Img
        self.txt2img_pipe = StableDiffusionPipeline.from_pretrained(
            self.model_id,
            torch_dtype=torch_dtype
        ).to(self.device)
        
        # Memory optimization (RAM / VRAM) requested
        self.txt2img_pipe.enable_attention_slicing()
        
        # 2. Img2Img pipeline: Create by sharing internal components
        self.img2img_pipe = StableDiffusionImg2ImgPipeline(
            vae=self.txt2img_pipe.vae,
            text_encoder=self.txt2img_pipe.text_encoder,
            tokenizer=self.txt2img_pipe.tokenizer,
            unet=self.txt2img_pipe.unet,
            scheduler=self.txt2img_pipe.scheduler,
            safety_checker=self.txt2img_pipe.safety_checker,
            feature_extractor=self.txt2img_pipe.feature_extractor
        ).to(self.device)
        self.img2img_pipe.enable_attention_slicing()
        print("Modèles chargés avec succès.")

    def generate(self, prompt: str, width: int, height: int, strength: float, init_image: Optional[Image.Image] = None, callback: Optional[Callable] = None) -> Image.Image:
        """Génère une image Txt2Img ou Img2Img selon la présence de init_image."""
        
        kwargs = {
            "prompt": prompt,
            "num_inference_steps": 15,
            "callback": callback,
            "callback_steps": 1
        }
        
        if init_image is not None:
            # Img2Img mode
            return self.img2img_pipe(
                image=init_image,
                strength=strength,
                **kwargs
            ).images[0]
        else:
            # Txt2Img mode
            return self.txt2img_pipe(
                width=width,
                height=height,
                **kwargs
            ).images[0]
