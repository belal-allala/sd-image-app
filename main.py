import os
import io
import json
import base64
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from diffusers import StableDiffusionPipeline
import torch

# ==========================================
#        SERVICE IMAGE (WEBSOCKETS READY)
# ==========================================

class ImageService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ImageService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.dtype = torch.float16 if self.device == "cuda" else torch.float32
        
        try:
            model_id = "runwayml/stable-diffusion-v1-5"
            self.pipeline = StableDiffusionPipeline.from_pretrained(
                model_id, torch_dtype=self.dtype, safety_checker=None
            )
            self.pipeline = self.pipeline.to(self.device)
            self.pipeline.enable_attention_slicing()
            print("[+] ImageService opérationnel.")
        except Exception as e:
            print(f"[-] Erreur Init : {e}")
            self.pipeline = None

    def generate_with_progress(self, prompt, width, height, label, websocket, loop):
        """
        Génère une image en envoyant les étapes via WebSocket.
        """
        steps = 15

        def step_callback(pipe, step_index, timestep, callback_kwargs):
            # Calcul du pourcentage pour l'image actuelle
            percent = int((step_index / steps) * 100)
            
            # Message de progression thread-safe
            asyncio.run_coroutine_threadsafe(
                websocket.send_json({
                    "type": "progress",
                    "label": label,
                    "value": percent
                }),
                loop
            )
            return callback_kwargs

        # Appel du pipeline avec callback
        result = self.pipeline(
            prompt,
            width=width,
            height=height,
            num_inference_steps=steps,
            callback_on_step_end=step_callback
        )
        
        image = result.images[0]
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

service = ImageService()

# ==========================================
#          CONFIGURATION APP
# ==========================================

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
#          ROUTE WEBSOCKET (REAL-TIME)
# ==========================================

@app.websocket("/ws/generate")
async def websocket_generate(websocket: WebSocket):
    await websocket.accept()
    loop = asyncio.get_running_loop()
    
    try:
        # Attente du message initial avec le prompt
        msg = await websocket.receive_json()
        prompt = msg.get("prompt")
        
        if not prompt:
            await websocket.send_json({"type": "error", "message": "Prompt vide."})
            return

        formats = [
            {"label": "WhatsApp Story", "width": 512, "height": 768},
            {"label": "Instagram Post", "width": 512, "height": 512},
            {"label": "Facebook Cover", "width": 768, "height": 512},
            {"label": "Standard Photo", "width": 640, "height": 480}
        ]

        for fmt in formats:
            # On exécute la génération lourde dans un thread séparé
            b64_img = await asyncio.to_thread(
                service.generate_with_progress, 
                prompt, fmt['width'], fmt['height'], fmt['label'], websocket, loop
            )
            
            # Envoi de l'image finale
            await websocket.send_json({
                "type": "image",
                "label": fmt['label'],
                "base64": f"data:image/png;base64,{b64_img}"
            })

        await websocket.send_json({"type": "complete"})

    except WebSocketDisconnect:
        print("[*] Client déconnecté.")
    except Exception as e:
        print(f"[-] Erreur WS : {e}")
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except: pass

# ==========================================
#          STATICS
# ==========================================

frontend_path = os.path.join(os.path.dirname(__file__), "frontend")
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
