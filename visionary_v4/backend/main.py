import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

# Imports depuis notre architecture modulaire engine/ et api/
from engine.generator import AdGenerator
from utils.image_utils import base64_to_pil, pil_to_base64
from api.websocket_manager import ConnectionManager
from api.routes import router as http_routes

# ----------------- INITIALISATION APP ----------------- #
app = FastAPI(
    title="Visionary V4", 
    description="Générateur de publicités de haut niveau via SDXL/ControlNet/IP-Adapter."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Remplacer par l'URL du front-end en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(http_routes, prefix="/api")

# Instance unique du gestionnaire de connexion WebSocket
manager = ConnectionManager()

# Instance de notre générateur qui lui gère en Singleton les modèles lourds
try:
    print("Démarrage du service d'IA...")
    generator = AdGenerator()
except Exception as e:
    print(f"Erreur d'amorçage : {e}")
    generator = None

# ----------------- ROUTE WEBSOCKET PRINCIPALE ----------------- #
@app.websocket("/ws/generate")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Nouveau client connecté au Socket de création.")

    try:
        while True:
            # 1. Attente et lecture des données JSON du Front-end
            data = await websocket.receive_json()
            
            # 2. Protection contre le SPAM (1 génération à la fois par websocket)
            if manager.is_generating(websocket):
                await manager.send_error(
                    websocket, 
                    "Vous avez déjà une génération publicitaire en cours."
                )
                continue

            # Verrouiller l'accès de ce client
            manager.set_generating(websocket, True)

            try:
                # 3. Extraction des paramètres réseau
                prompt = data.get("prompt", "")
                base64_images = data.get("images", [])
                format_choice = data.get("format", "post") # 'post', 'story', 'landscape'
                quality = data.get("quality", "standard")  # 'standard', 'high', 'pro'

                # Validation
                if not prompt or not base64_images:
                    await manager.send_error(websocket, "Paramètres incomplets: 'prompt' et 'images' requis.")
                    manager.set_generating(websocket, False)
                    continue

                # Mapping dynamique des qualités (Si pro/high -> high, si standard -> fast)
                mapped_quality = "high" if "high" in quality or "pro" in quality else "fast"

                # 4. Traduction des Images: Base64 -> PIL (Utilitaire de l'Etape 1)
                pil_inputs = []
                for b64 in base64_images:
                    pil_inputs.append(base64_to_pil(b64))

                loop = asyncio.get_running_loop()

                # 5. Injection de la Callback de progression
                def progression_sync_callback(step: int, total_steps: int, progress_pct: float):
                    # Rappel : le moteur s'exécute dans un Thread (bloquant pour asyncio)
                    # On utilise call_soon_threadsafe pour remettre le travail asynchrone sur la boucle API
                    asyncio.run_coroutine_threadsafe(
                        manager.send_progress(websocket, progress_pct, message=f"Etape {step}/{total_steps}..."),
                        loop
                    )

                # 6. Exécution du méga-générateur dans un Thread séparé 
                # !!! Crucial pour que FastAPI puisse continuer à servir d'autres clients !!!
                final_img_pil = await asyncio.to_thread(
                    generator.generate,
                    prompt=prompt,
                    list_of_images=pil_inputs,
                    format_choice=format_choice,
                    quality_level=mapped_quality,
                    callback=progression_sync_callback
                )

                # 7. Renvoi des résultats
                if final_img_pil:
                    final_base64 = pil_to_base64(final_img_pil)
                    await manager.send_image(websocket, final_base64, format_choice)
                else:
                    await manager.send_error(websocket, "Echec inattendu du moteur : Plus de VRAM ou image corrompue.")

            except Exception as task_err:
                print(f"Erreur durant l'assemblage : {task_err}")
                await manager.send_error(websocket, f"Erreur critique interne : {str(task_err)}")
            
            finally:
                # IMPORTANT : Toujours déverrouiller la connexion après
                manager.set_generating(websocket, False)

    except WebSocketDisconnect:
        print("La connexion cliente a été coupée.")
        manager.disconnect(websocket)
    except Exception as e:
        print(f"Rupture de socket: {e}")
        manager.disconnect(websocket)

import os
from fastapi.staticfiles import StaticFiles

# ----------------- SERVICE DU FRONTEND ----------------- #
# L'utilisation de __file__ permet de résoudre le chemin de manière dynamique
# indépendamment d'où le script est lancé.
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

# Démarrage direct possible via python main.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
