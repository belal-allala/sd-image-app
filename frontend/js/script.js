document.addEventListener('DOMContentLoaded', () => {
    // Récupération des éléments du DOM
    const promptInput = document.getElementById('prompt-input');
    const generateBtn = document.getElementById('generate-btn');
    const btnText = document.querySelector('.btn-text');
    const loader = document.querySelector('.loader');
    
    const stepsSlider = document.getElementById('steps-slider');
    const stepsValue = document.getElementById('steps-value');
    
    const resultSection = document.getElementById('result-section');
    const actionsSection = document.getElementById('actions-section');
    const downloadBtn = document.getElementById('download-btn');
    
    // Nouveaux éléments pour la progression
    const progressContainer = document.getElementById('progress-container');
    const progressFill = document.getElementById('progress-fill');
    const progressPercent = document.getElementById('progress-percent');
    
    // Garder en mémoire l'image générée
    let currentImageBlob = null;

    // Mise à jour de l'affichage du slider en temps réel
    stepsSlider.addEventListener('input', (e) => {
        stepsValue.textContent = e.target.value;
    });

    /**
     * Gère l'état visuel de l'interface en mode "Chargement"
     */
    const setGeneratingState = (isGenerating) => {
        generateBtn.disabled = isGenerating;
        promptInput.disabled = isGenerating;
        stepsSlider.disabled = isGenerating;

        if (isGenerating) {
            // Cacher le texte, montrer le spinner
            btnText.classList.add('hidden');
            loader.classList.remove('hidden');
            
            // Animation personnalisée pour faire patienter
            resultSection.innerHTML = `
                <div class="placeholder-content step-pulse">
                    <p style="font-size:1.1rem; color:#fff">💫 Génération en cours...</p>
                    <small style="opacity:0.6; display:block; margin-top:8px;">L'IA crée votre image, veuillez patienter.</small>
                </div>
            `;
            
            actionsSection.classList.add('hidden');
            resultSection.style.border = '2px dashed var(--glass-border)';
            
            // Ajout dynamique de la keyframe si elle n'existe pas
            if (!document.getElementById('anim-style')) {
                const style = document.createElement('style');
                style.id = 'anim-style';
                style.innerHTML = `
                    @keyframes pulseFeedback {
                        0% { opacity: 0.5; transform: scale(0.98); }
                        50% { opacity: 1; transform: scale(1.02); }
                        100% { opacity: 0.5; transform: scale(0.98); }
                    }
                    .step-pulse { animation: pulseFeedback 2s infinite ease-in-out; }
                `;
                document.head.appendChild(style);
            }

        } else {
            // Remettre à la normale
            btnText.classList.remove('hidden');
            loader.classList.add('hidden');
        }
    };

    /**
     * Affiche une erreur dans la zone de résultat
     */
    const showError = (message) => {
        resultSection.innerHTML = `
            <div class="placeholder-content" style="color: #ef4444;">
                <p>⚠️ Erreur : ${message}</p>
                <small style="opacity:0.7">Vérifiez la console ou relancez le serveur.</small>
            </div>
        `;
        progressContainer.classList.add('hidden');
    };

    /**
     * Appelle le Backend via WebSocket pour une progression en temps réel
     */
    const generateImage = () => {
        const prompt = promptInput.value.trim();
        if (!prompt) return;

        const steps = parseInt(stepsSlider.value);
        setGeneratingState(true);

        // Initialisation de la barre de progression
        progressContainer.classList.remove('hidden');
        progressFill.style.width = '0%';
        progressPercent.textContent = '0%';

        // Détection du protocole automatique
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/generate`;
        
        const socket = new WebSocket(wsUrl);

        socket.onopen = () => {
            console.log("[*] WebSocket connecté, envoi du prompt...");
            socket.send(JSON.stringify({ prompt, steps }));
        };

        socket.onmessage = async (event) => {
            const data = JSON.parse(event.data);

            if (data.type === 'progress') {
                const val = data.value;
                progressFill.style.width = `${val}%`;
                progressPercent.textContent = `${val}%`;
            } else if (data.type === 'finish') {
                const imgData = data.image; // Base64
                
                // Conversion en blob pour le bouton de téléchargement
                const res = await fetch(imgData);
                currentImageBlob = await res.blob();
                
                renderImage(imgData);
                socket.close();
            } else if (data.type === 'error') {
                showError(data.message);
                socket.close();
            }
        };

        socket.onerror = (error) => {
            console.error('WebSocket Error:', error);
            showError('Échec de la connexion WebSocket.');
        };

        socket.onclose = () => {
            console.log("[*] WebSocket fermé.");
            setGeneratingState(false);
        };
    };

    /**
     * Affiche l'image dans l'UI une fois reçue
     */
    const renderImage = (imageUrl) => {
        resultSection.innerHTML = ''; // Nettoie le conteneur
        
        const img = document.createElement('img');
        img.src = imageUrl;
        img.className = 'generated-image';
        
        // Effet de fade-in gracieux une fois chargée par le navigateur
        img.onload = () => {
            img.classList.add('loaded');
        };

        resultSection.appendChild(img);
        resultSection.style.border = 'none'; // Retire la bordure pointillée
        
        // Affiche le bouton de téléchargement
        actionsSection.classList.remove('hidden');
    };

    /**
     * Télécharge le Blob en tant qu'image PNG locale
     */
    const downloadImage = () => {
        if (!currentImageBlob) return;
        
        const url = URL.createObjectURL(currentImageBlob);
        const a = document.createElement('a');
        a.href = url;
        
        // Nom de fichier intelligent basé sur le prompt
        const safePrompt = promptInput.value.replace(/[^a-z0-9]/gi, '_').substring(0, 20).toLowerCase();
        a.download = `visionary_${safePrompt}.png`;
        
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    };

    // Événements
    generateBtn.addEventListener('click', generateImage);
    
    // Support de la touche "Entrée"
    promptInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            generateImage();
        }
    });
    
    downloadBtn.addEventListener('click', downloadImage);
});
