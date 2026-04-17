import torch
from diffusers import StableDiffusionXLControlNetPipeline, ControlNetModel

class ModelLoader:
    _instance = None

    def __new__(cls):
        """Assure que le ModelLoader est un Singleton."""
        if cls._instance is None:
            cls._instance = super(ModelLoader, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialise et charge les modèles avec optimisation de la VRAM."""
        print("="*70)
        print("Initialisation du ModelLoader (SDXL + ControlNet + IP-Adapter)...")
        print("Attention (Premier Lancement) : Le téléchargement des modèles (SDXL,")
        print("ControlNet, IP-Adapter) va commencer (environ 6-10 Go de données).")
        print("Veuillez patienter, cela peut prendre un certain temps...")
        print("="*70)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        # Utilisation de fp16 pour réduire l'empreinte mémoire
        self.torch_dtype = torch.float16 if self.device == "cuda" else torch.float32
        self.pipeline = None

        try:
            # 1. Chargement de ControlNet (Canny pour SDXL)
            print("Chargement du modèle ControlNet (Canny)...")
            controlnet = ControlNetModel.from_pretrained(
                "diffusers/controlnet-canny-sdxl-1.0",
                torch_dtype=self.torch_dtype,
                variant="fp16" if self.torch_dtype == torch.float16 else None,
                use_safetensors=True
            )

            # 2. Chargement de SDXL (Base) optimisé (Par exemple avec SDXL-Lightning)
            print("Chargement de la pipeline de base SDXL...")
            self.pipeline = StableDiffusionXLControlNetPipeline.from_pretrained(
                "stabilityai/stable-diffusion-xl-base-1.0",
                controlnet=controlnet,
                torch_dtype=self.torch_dtype,
                variant="fp16" if self.torch_dtype == torch.float16 else None,
                use_safetensors=True
            )

            # 3. Chargement de l'IP-Adapter Plus pour SDXL
            print("Chargement de l'IP-Adapter pour SDXL...")
            # Chargement natif d'IP-Adapter au sein des diffusers
            self.pipeline.load_ip_adapter(
                "h94/IP-Adapter", 
                subfolder="sdxl_models", 
                weight_name="ip-adapter-plus_sdxl_vit-h.bin"
            )

            # 4. Optimisations mémoires strictes pour fonctionner avec <= 12 Go VRAM
            print("Optimisation de la VRAM en cours...")
            if self.device == "cuda":
                # Offload du modèle vers le CPU pendant qu'il n'est pas utilisé
                self.pipeline.enable_model_cpu_offload()

                # Slice des calculs du VAE pour réduire les pics de mémoire
                self.pipeline.enable_vae_slicing()
                self.pipeline.enable_vae_tiling()

                # Attention efficace (via xformers)
                try:
                    self.pipeline.enable_xformers_memory_efficient_attention()
                    print("Xformers memory efficient attention activée.")
                except Exception as e:
                    print(f"Xformers n'est pas disponible, génération classique. ({e})")
            
            print("Modèles chargés et prêts.")
            
        except Exception as e:
            print(f"Erreur lors du chargement des modèles : {e}")
            raise e

    def get_pipeline(self) -> StableDiffusionXLControlNetPipeline:
        """Retourne la pipeline de génération SDXL."""
        if self.pipeline is None:
            raise RuntimeError("La pipeline n'a pas été initialisée.")
        return self.pipeline
