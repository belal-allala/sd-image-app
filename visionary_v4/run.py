import sys
import subprocess

def check_dependencies():
    print("Vérification des dépendances pour Visionary V4...")
    
    missing = []
    
    try: import torch
    except ImportError: missing.append("torch")
        
    try: import diffusers
    except ImportError: missing.append("diffusers")
        
    try: import fastapi
    except ImportError: missing.append("fastapi")
        
    try: import uvicorn
    except ImportError: missing.append("uvicorn")
        
    try: import rembg
    except ImportError: missing.append("rembg")
        
    try: import cv2
    except ImportError: missing.append("opencv-python")
        
    try: import PIL
    except ImportError: missing.append("pillow")
        
    try: import transformers
    except ImportError: missing.append("transformers")
        
    try: import accelerate
    except ImportError: missing.append("accelerate")
        
    if missing:
        print(f"\n❌ Erreur : Des bibliothèques sont manquantes : {', '.join(missing)}")
        print("👉 Veuillez exécuter : pip install -r requirements.txt\n")
        sys.exit(1)
        
    print("✅ Toutes les dépendances sont installées.")

if __name__ == "__main__":
    check_dependencies()
    print("🚀 Lancement du serveur unifié Visionary V4 (Uvicorn)...")
    
    try:
        import os
        # Lance Uvicorn depuis le dossier backend interne
        backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
        subprocess.run(["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"], cwd=backend_dir)
    except KeyboardInterrupt:
        print("\nArrêt du serveur Visionary V4.")
