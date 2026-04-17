# Visionary V4 🚀 - Pro AI Ad Studio

Visionary V4 est un générateur professionnel d'images publicitaires propulsé par l'Intelligence Artificielle. Il fusionne plusieurs modèles de pointe (SDXL, ControlNet et IP-Adapter) au sein d'une architecture asynchrone hautement modulaire permettant un suivi en temps réel.

---

## 🏛️ Architecture du Projet

L'écosystème entier (Front-end Web et Back-end IA) a été unifié sous un même prisme de service. L'architecture est totalement modulaire (Clean Architecture) via un fonctionnement asynchrone (FastAPI + Asyncio) pour que les calculs de carte graphique ne bloquent pas le serveur de communication.

### 1. Le Frontend (Interface Utilisateur)
Situé dans `/frontend/`, c'est le point d'interaction web "Zero-Framework" (du JavaScript pur Vanilla) se voulant ultra-léger et réactif.
- **Design Studio** : Habillage complet CSS "Dark Mode" géré en Flexbox.
- **`ui_manager.js`** : Contrôleur logique qui s'occupe de gérer le glisser-déposer de vos photos (Drag & Drop), la limite imposée de 9 d'images, et la mémorisation du contexte d'état (Formats et Qualité).
- **`socket_client.js`** : L'ingénieur réseau côté client. Il converse exclusivement en **WebSockets** (JSON bidirectionnel) via `ws://` avec l'API pour remonter les pourcentages de construction d'image à l'écran sans aucun rechargement HTTP classique.

### 2. Le Backend (Orchestre et API Serveur)
Point d'entrée du Python. Il gère l'orchestration depuis le dossier `/backend/`.
- **Mécanisme Statique Inclusif (`main.py`)** : Monte la route asynchrone du WebSocket, mais s'occupe de servir lui-même (`StaticFiles`) le frontend sur le port Web commun `localhost:8000`. Cela efface les problèmes diaboliques de permissions CORS !
- **Délégation Parabolique (`asyncio.to_thread`)** : Quand l'IA met 30 secondes à générer une photo, `main.py` déplace le lourd processus de calcul dans un Thread séparé. Ainsi, le système API reste "disponible" et "réveillé" pour d'autres commandes.

### 3. Le Moteur IA (Layer `/engine/`)
Constitue la tour de contrôle du process Stable Diffusion XL.
- **`model_loader.py` (Singleton Pattern)** : Garantit que le colosse `Stable Diffusion XL 1.0` n'est décompressé qu'une et qu'une seule fois dans la RAM/VRAM de la carte graphique.
- **Hybridation ControlNet + IP-Adapter Plus** : 
    - Le **ControlNet (Canny)** ingère l'image produit originale pour dessiner les arêtes stricts. Peu importe le fond que l'IA va générer, l'allure exacte du produit (Ex: une bouteille galbée) ne changera pas d'un pixel.
    - L'**IP Adapter** capte l'essence et le style à partir des 9 petites photos de références pour faire "comprendre" les textures exactes et les couleurs d'un produit (les logos imprimés sur une boite, le relief d'une chaussure).
- **`generator.py`** : Lance l'inférence. Il gère un Callback de progression (les "steps" d'IA) calculant un $\%$ mathématiquement remonté et synchronisé à `/api/websocket_manager.py`.

---

## 📋 Prérequis Matériels

- **Python 3.9+**
- **Carte Graphique NVIDIA** avec de préférence **12 Go de VRAM minimum**. Le script contient nativement les verrous d'optimisation (précision `fp16`, déchargement `enable_model_cpu_offload`, gestion `attention_slicing` via xFormers).
- Vous devez avoir le Toolkit NVIDIA CUDA d'installé.

---

## 🛠️ Installation Initiale

1. Placez votre terminal à la racine `\visionary_v4`.
2. Installez les packages fondamentaux via le fichier prévu :
```bash
pip install -r requirements.txt
```

---

## 🚀 Le Lancement Auto

J'ai créé pour vous un lanceur magique qui lance la commande de serveur en vérifiant que n'avez oublié aucune librairie. Vous n'avez qu'à lancer ça à chaque fois que vous voulez faire de l'IA :

```bash
python run.py
```

> **⚠️ PREMIER LANCEMENT = BIG DATA:**
> Lors du premier démarrage exact de l'application (et uniquement le premier!), les librairies Python de l'IA iront interroger HuggingFace pour acquérir physiquement les fichiers binaires des modèles (SDXL, ControlNet Canny, IP-Adapter). 
> **Une attente de téléchargement estimée entre 6 et 10 Go d'espace est à prévoir** en direct dans la console ! Prenez un café ! ☕

---

## 🖥️ Comment Utiliser Visionary V4 ?

Dès lors que la console indique : `Uvicorn running on http://0.0.0.0:8000` :

1. **Surfez !** Ouvrez simplement Edge, Chrome ou Firefox à l'adresse locale `http://localhost:8000`. (Grâce à l'unification, c'est l'API elle-même qui enverra la belle interface "Dark Studio").
2. **Upload (À Gauche)** : Glissez-déposez de **1 à 9 photos strictes** du produit. Varier les angles est très utile pour un impact IP-Adapter profond.
3. **Contexte (Prompt)** : Décrivez l'annonce finale que vous souhaitez *(ex: "Produit posé sur le bitume gelé, ambiance cyberpunk nocturne, éclairage néon violet, rendu 8k photoréaliste".)*
4. **Réglages** : Cochez avec les beaux boutons si c'est pour du Post carré ou de la Story Instagram, et choisissez un rendu `Rapide` (30 étapes) ou `Pro` (45 étapes de finition).
5. Appuyez sur **GÉNÉRER LA PUBLICITÉ**.
6. Observez l'IA réfléchir en temps réel en direct sur via la cartouche de rendu sur la fenêtre de droite !
