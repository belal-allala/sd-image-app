import os
import base64
import asyncio
from fastapi import FastAPI, Response, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from diffusers import StableDiffusionPipeline
import torch
import io

# Initialisation de l'application FastAPI
app = FastAPI(title="Visionary - Stable Diffusion AI")

# Sécurité : Configuration du middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Optimisation : Détection du GPU (CUDA) et sélection du type de données
device = "cuda" if torch.cuda.is_available() else "cpu"
dtype = torch.float16 if device == "cuda" else torch.float32

print(f"[*] Initialisation : Chargement du modèle sur {device.upper()} avec {dtype}...")

# Chargement du modèle
try:
    model_id = "runwayml/stable-diffusion-v1-5"
    pipeline = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=dtype)
    pipeline = pipeline.to(device)
    print("[+] Modèle chargé avec succès !")
except Exception as e:
    print(f"[-] Erreur au chargement du modèle: {e}")
    pipeline = None

# ==========================================
#          ROUTES API (BACKEND)
# ==========================================

@app.get("/api/generate")
def generate_image(prompt: str, steps: int = 20):
    """
    Route API classique (HTTP) pour générer une image.
    """
    if not pipeline:
        return Response(content="Modèle non initialisé.", status_code=500)
    
    print(f"[*] Génération (HTTP) en cours pour : '{prompt}' ({steps} étapes)")
    try:
        result = pipeline(prompt, num_inference_steps=steps)
        image = result.images[0]
        
        memory_stream = io.BytesIO()
        image.save(memory_stream, format="PNG")
        memory_stream.seek(0)
        
        return Response(content=memory_stream.getvalue(), media_type="image/png")
    except Exception as e:
        print(f"[-] Erreur de génération : {e}")
        return Response(content=str(e), status_code=500)

@app.websocket("/ws/generate")
async def websocket_generate(websocket: WebSocket):
    """
    Route WebSocket pour générer une image avec progression en temps réel.
    """
    await websocket.accept()
    loop = asyncio.get_running_loop()
    
    try:
        # Réception des paramètres
        params = await websocket.receive_json()
        prompt = params.get("prompt")
        steps = params.get("steps", 20)
        
        if not pipeline:
            await websocket.send_json({"type": "error", "message": "Modèle non initialisé."})
            await websocket.close()
            return

        print(f"[*] Génération (WS) en cours : '{prompt}'")

        # Callback pour envoyer la progression
        def progress_callback(step, timestep, latents):
            percent = int(((step + 1) / steps) * 100)
            # Thread-safe send
            asyncio.run_coroutine_threadsafe(
                websocket.send_json({"type": "progress", "value": min(percent, 100)}),
                loop
            )

        # Exécution dans un thread pour ne pas bloquer le loop
        def run_inference():
            return pipeline(
                prompt, 
                num_inference_steps=steps, 
                callback=progress_callback, 
                callback_steps=1
            )

        result = await asyncio.to_thread(run_inference)
        image = result.images[0]
        
        # Encodage en base64
        memory_stream = io.BytesIO()
        image.save(memory_stream, format="PNG")
        img_str = base64.b64encode(memory_stream.getvalue()).decode("utf-8")
        
        # Envoi de l'image finale
        await websocket.send_json({
            "type": "finish",
            "image": f"data:image/png;base64,{img_str}"
        })

    except WebSocketDisconnect:
        print("[*] WebSocket déconnecté par le client.")
    except Exception as e:
        print(f"[-] Erreur WebSocket : {e}")
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except:
            pass

# ==========================================
#          FRONTEND (STATIC FILES)
# ==========================================

frontend_path = os.path.join(os.path.dirname(__file__), "frontend")

try:
    # Créer le répertoire si cela n'existe pas en memoire (juste par precaution)
    os.makedirs(frontend_path, exist_ok=True)
    # Lier le dossier frontend à la racine
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
    print(f"[+] Frontend mapé au dossier : {frontend_path}")
except Exception as e:
    print(f"[-] Erreur lors du montage du frontend : {e}")
