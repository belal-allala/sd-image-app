# Visionary - Stable Diffusion Image Generator 🎨

Visionary est une application web de génération d'images par Intelligence Artificielle (Text-to-Image) qui utilise le modèle **Stable Diffusion v1.5**. Elle est propulsée par un backend **FastAPI** très performant et offre une interface utilisateur moderne (style *Glassmorphism*) développée en HTML/CSS/JS.

## 🌟 Fonctionnalités

- **Text-to-Image** : Transformez de simples descriptions textuelles (*prompts*) en images détaillées.
- **Curseur de Qualité** : Ajustez facilement le nombre d'étapes d'inférence via un curseur fluide pour privilégier la rapidité ou la qualité des détails.
- **Accélération matérielle** : Détection automatique de votre carte graphique (NVIDIA CUDA) pour des générations accélérées optimisées en utilisant `float16`. 
- **Design Premium** : Interface dynamique avec des effets de verre dépoli, arrière-plan galactique animé et retours visuels soignés.
- **Téléchargement Local** : Sauvegardez instantanément vos créations sur votre machine en un clic.

---

## 🏗️ Architecture du Projet

Le projet a été pensé pour être simple et robuste. FastAPI gère à la fois l'API (pour générer l'image avec Python) et la distribution des fichiers de l'interface utilisateur.

```text
sd-image-app/
│
├── main.py                # Backend principal (IA + Serveur)
├── README.md              # Documentation du projet
└── frontend/              # Fichiers de l'interface utilisateur visuelle
    ├── index.html         # Structure de l'application Web
    ├── css/
    │   └── style.css      # Design esthétique et animations
    └── js/
        └── script.js      # Logique, requêtes en tâche de fond (Fetch API) 
```

---

## 🚀 Guide d'Installation et d'Utilisation

### 1. Prérequis

Assurez-vous d'avoir installé sur votre machine :
- **Python 3.8+**
- (Optionnel mais fortement recommandé) Une carte graphique NVIDIA avec les pilotes à jour pour des générations d'images beaucoup plus rapides.

### 2. Configuration de l'environnement (Windows)

Ouvrez un terminal (PowerShell) dans le dossier du projet, puis créez et activez un environnement virtuel pour isoler le projet :

```powershell
# 1. Créer l'environnement virtuel
python -m venv venv

# 2. L'activer
.\venv\Scripts\Activate.ps1
```

> **Aide Windows :** Si l'activation échoue avec un texte rouge (scripts désactivés), exécutez la commande `Set-ExecutionPolicy Unrestricted -Scope CurrentUser`, puis réessayez de l'activer.

### 3. Installation des dépendances

Installez les bibliothèques requises pour faire tourner l'IA et le serveur local :

```powershell
pip install fastapi uvicorn torch diffusers transformers accelerate
```

### 4. Démarrer l'application

Vérifiez que votre environnement virtuel `(venv)` est bien visible sur la gauche de votre terminal, puis lancez le serveur :

```powershell
uvicorn main:app --reload
```

> **Attention au premier lancement :** Le programme devra télécharger automatiquement le modèle de l'Intelligence Artificielle en mémoire (environ 4 Go). Cela peut prendre quelques minutes. Les lancements suivants seront presque instantanés.

### 5. Utiliser l'Interface

1. Ouvrez votre navigateur web favori et naviguez vers l'adresse magique : **[http://localhost:8000](http://localhost:8000)**
2. Dans la barre de recherche textuelle, décrivez précisément votre idée (ex: *"Une ville cyberpunk sous la pluie, réaliste, 8k"*). Plus la description est précise, meilleure sera l'association avec l'IA.
3. Cliquez sur le bouton **Générer** (et attendez que l'IA rêve de votre image en tâche de fond !).
4. Profitez de l'oeuvre et sauvegardez-la grâce au bouton **Sauvegarder l'image**.

---

*Bonne génération ! Propulsé par Python et l'approche de développement par composants séparés.*
