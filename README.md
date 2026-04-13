# Visionary - Stable Diffusion AI (v4.0 WebSocket) 🎨✨

Visionary est une application web de pointe pour la génération d'images par Intelligence Artificielle. Cette version exploite les **WebSockets** pour offrir une expérience ultra-réactive avec un suivi de progression étape par étape.

## 🌟 Nouvelles Fonctionnalités (v4.0)

- **Suivi Granulaire** : Voyez l'avancement exact (0-100%) de la génération pour chaque format.
- **Ratios Réels** : L'interface respecte les dimensions physiques de chaque format (Vertical pour Story, Carré pour Instagram, Large pour Facebook).
- **Architecture Modulaire** : Code structuré en services (ImageService, SocketService, UIManager) pour une performance maximale.
- **WebSocket Dual-Way** : Communication bidirectionnelle entre le client et le serveur.

---

## 🏗️ Formats de Sortie Automatiques

À chaque session, Visionary génère simultanément :
1.  **WhatsApp Story** : 512x768 (Ratio 2:3 vertical)
2.  **Instagram Post** : 512x512 (Ratio 1:1 carré)
3.  **Facebook Cover** : 768x512 (Ratio 3:2 large)
4.  **Standard Photo** : 640x480 (Ratio 4:3 classique)

---

## 🚀 Guide d'Utilisation

### 1. Installation des dépendances
Ouvrez votre terminal et installez les bibliothèques nécessaires :
```powershell
pip install fastapi uvicorn websockets torch diffusers transformers accelerate
```

### 2. Lancement du serveur
Lancez l'application avec Uvicorn :
```powershell
uvicorn main:app --reload
```

### 3. Utilisation de l'Interface
1. Accédez à **[http://localhost:8000](http://localhost:8000)**.
2. Saisissez une description textuelle (ex: *"Un astronaute pêchant sur la lune, style aquarelle"*).
3. Cliquez sur **Démarrer la Session**.
4. **Observez les barres de progression** sur chaque carte : elles reflètent le travail en temps réel de l'IA.
5. Une fois l'image apparue, cliquez sur le **bouton de téléchargement** (icône flèche) pour sauvegarder le format souhaité.

---

## 💡 Conseils Techniques
- **Accélération GPU** : Si vous avez une carte NVIDIA, l'application utilisera automatiquement CUDA pour des générations 10x plus rapides.
- **Mode CPU** : Sur CPU, prévoyez environ 1 à 2 minutes par pack de 4 images. La barre de progression vous permet de suivre l'état sans deviner.

---
*Développé avec passion pour l'IA générative. Version 4.0.*
