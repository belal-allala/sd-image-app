from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import asyncio
import json

from engine import ImageEngine
from utils import base64_to_pil, pil_to_base64, preprocess_image

app = FastAPI(title="Visionary V3 - Hybrid AI Generator")

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instance globale (Singleton) du moteur d'IA
engine = ImageEngine()

@app.websocket("/ws/generate")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_text()
        request_data = json.loads(data)
        
        prompt = request_data.get("prompt", "")
        base64_init_image = request_data.get("init_image", None)
        formats = request_data.get("formats", [])
        strength = request_data.get("strength", 0.75)
        
        for fmt in formats:
            format_name = fmt.get("name", "Unknown")
            width = fmt.get("width", 512)
            height = fmt.get("height", 512)
            
            init_img_pil = None
            if base64_init_image:
                init_img_pil = base64_to_pil(base64_init_image)
                init_img_pil = preprocess_image(init_img_pil, width, height)
            
            # Boucle d'événements courante pour la notification inter-threads
            loop = asyncio.get_running_loop()
            
            def notify_progress(step: int, total_steps: int):
                progress_pct = int(((step + 1) / total_steps) * 100)
                msg = {
                    "type": "progress",
                    "format": format_name,
                    "progress": progress_pct,
                    "step": step + 1,
                    "total_steps": total_steps
                }
                asyncio.run_coroutine_threadsafe(websocket.send_json(msg), loop)

            # Wrapper pour la callback de diffusers
            def step_callback(step: int, timestep: int, latents):
                notify_progress(step, 15)

            # Exécution de la génération dans un thread
            result_image = await asyncio.to_thread(
                engine.generate,
                prompt=prompt,
                width=width,
                height=height,
                strength=strength,
                init_image=init_img_pil,
                callback=step_callback
            )
            
            # Formatage de l'image finale
            result_b64 = pil_to_base64(result_image)
            await websocket.send_json({
                "type": "image",
                "format": format_name,
                "image": result_b64
            })
            
        await websocket.send_json({"type": "complete"})
        
    except WebSocketDisconnect:
        print("Client déconnecté")
    except Exception as e:
        print(f"Erreur WebSocket: {e}")
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except:
            pass

# Montage du dossier statique pour le frontend
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
