document.addEventListener('DOMContentLoaded', () => {
    console.log("Initialisation de l'Orchestrateur WebSocket Visionary V4...");

    // ---------------- UI ELEMENTS ----------------
    const statusDot = document.getElementById('socket-status-dot');
    const statusText = document.getElementById('socket-status-text');
    const generateBtn = document.getElementById('generate-btn');
    const promptInput = document.getElementById('prompt-input');
    const renderContainer = document.getElementById('render-container');
    const emptyState = document.getElementById('empty-state');

    // ---------------- ETAT TECHNIQUE ----------------
    let ws = null;
    let isGenerating = false;
    let currentRenderCardId = null; 

    // ============================================================== //
    // 1. GESTION DE LA CONNEXION WEBSOCKET                           //
    // ============================================================== //
    
    function connectSocket() {
        // Résout dynamiquement l'adresse serveur depuis le navigateur (très souple en réseau local)
        const host = window.location.host || "localhost:8000";
        const wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:";
        const wsUrl = `${wsProtocol}//${host}/ws/generate`;
        
        ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            console.log("Connecté au serveur de génération.");
            statusDot.classList.add('connected');
            statusText.textContent = "Connecté au Studio IA";
            statusText.style.color = "var(--success-color)";
            
            // On s'assure de débloquer le bouton uniquement si on n'était pas déjà bloqué
            if (!isGenerating && generateBtn) {
                generateBtn.disabled = false;
                generateBtn.textContent = 'GÉNÉRER LA PUBLICITÉ';
            }
        };

        ws.onclose = () => {
            console.warn("Connexion perdue avec le serveur IA.");
            statusDot.classList.remove('connected');
            statusText.textContent = "Hors ligne (Reconnexion en cours...)";
            statusText.style.color = "var(--danger-color)";
            
            if (generateBtn) {
                generateBtn.disabled = true;
                generateBtn.textContent = 'SYSTÈME DÉCONNECTÉ';
            }
            
            // Mécanisme robuste : Reconnexion automatique toutes les 3 secondes
            setTimeout(connectSocket, 3000);
        };

        ws.onerror = (err) => {
            console.error("Erreur de liaison réseau :", err);
        };

        // GESTION DES EVENEMENTS SERVEUR INTRANTS
        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                console.log("Signal reçu :", data.type);

                switch (data.type) {
                    case 'progress':
                        renderProgressIndicator(data);
                        break;
                    case 'image':
                        renderFinalArtwork(data);
                        break;
                    case 'error':
                        triggerErrorState(data);
                        break;
                    default:
                        console.warn("Payload JSON inconnu reçu :", data);
                }
            } catch (err) {
                console.error("Impossible de lire la donnée WebSocket :", err);
            }
        };
    }


    // ============================================================== //
    // 2. ENVOI DE LA COMMANDE DE GENERATION                          //
    // ============================================================== //

    generateBtn.addEventListener('click', () => {
        // Récupérer le prompt
        const promptText = promptInput.value.trim();
        
        // Récupérer les variables mémorisées par ui_manager.js
        const uiState = window.appUIState;

        // --- VALIDATION DEUX NIVEAUX --- //
        if (!promptText) {
            alert("L'Intelligence Artificielle a besoin d'une description solide pour le Prompt Créatif.");
            promptInput.focus();
            return;
        }

        if (!uiState.images || uiState.images.length === 0) {
            alert("Glissez-déposez au moins 1 image du produit pour que le ControlNet l'analyse.");
            return;
        }

        if (ws.readyState !== WebSocket.OPEN) {
            alert("Le serveur n'est pas accessible pour le moment. Veuillez patienter.");
            return;
        }

        // FORMER LE JSON EXACT ATTENDU PAR FastAPI (main.py)
        const generatePayload = {
            prompt: promptText,
            images: uiState.images,
            format: uiState.format,
            quality: uiState.quality
        };

        console.log("🚀 Lancement vers le Backend FastAPI :", {
            format: generatePayload.format,
            quality: generatePayload.quality,
            images_count: generatePayload.images.length
        });

        // Verrouiller la page anti-spam
        isGenerating = true;
        generateBtn.disabled = true;
        generateBtn.textContent = "CRÉATION DE L'ANNONCE EN COURS...";
        
        // Retirer l'état visuel "vide" de l'écran droit
        if (emptyState) emptyState.style.display = 'none';

        // Créer l'UI graphique dynamique pour voir l'évolution
        buildProgressCard(uiState.format);

        // ENVOI RESEAU 
        ws.send(JSON.stringify(generatePayload));
        
        // UX : Scroller doucement la page pour se concentrer sur le résultat sur les petits écrans
        renderContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });


    // ============================================================== //
    // 3. LOGIQUE UX DE RENDEMENT RESPONSIVE                          //
    // ============================================================== //

    function buildProgressCard(formatType) {
        // Créer un ID traçable unique
        currentRenderCardId = 'v4_card_' + Date.now();
        
        const cardTemplate = `
            <div id="${currentRenderCardId}" class="render-card" style="opacity: 0; transform: translateY(20px); transition: all 0.4s ease;">
                <div class="render-header">
                    <h3>Projet Studio V4</h3>
                    <span class="render-format-tag">${formatType}</span>
                </div>
                
                <div class="render-zone" id="zone_${currentRenderCardId}">
                    <div style="padding: 20px 0;">
                        <h2 class="render-percentage" id="pct_${currentRenderCardId}">0 %</h2>
                        <div class="progress-track" style="margin: 15px 0;">
                            <div class="progress-fill" id="bar_${currentRenderCardId}"></div>
                        </div>
                        <p class="render-message" id="msg_${currentRenderCardId}">Allumage des cœurs Tensor...</p>
                    </div>
                </div>
                
                <div id="btn-group_${currentRenderCardId}" style="display:none; text-align:right; margin-top:15px;">
                    <!-- Futur Bouton Télécharger -->
                </div>
            </div>
        `;

        renderContainer.insertAdjacentHTML('afterbegin', cardTemplate); 
        
        // Faire glisser la carte avec style
        setTimeout(() => {
            const element = document.getElementById(currentRenderCardId);
            if(element) {
                element.style.opacity = 1;
                element.style.transform = 'translateY(0)';
            }
        }, 50);
    }

    function renderProgressIndicator(data) {
        if (!currentRenderCardId) return;

        const elPercent = document.getElementById(`pct_${currentRenderCardId}`);
        const elBar = document.getElementById(`bar_${currentRenderCardId}`);
        const elMsg = document.getElementById(`msg_${currentRenderCardId}`);

        if (elPercent && elBar) {
            elPercent.textContent = `${data.value} %`;
            elBar.style.width = `${data.value}%`;
            if (data.message) {
                elMsg.innerHTML = `${data.message} <span style="display:inline-block; animation: pulse 1.5s infinite;">...</span>`;
            }
        }
    }

    function renderFinalArtwork(data) {
        console.log("Rendu final capté ! Format =", data.format);
        if (!currentRenderCardId) return;

        const zone = document.getElementById(`zone_${currentRenderCardId}`);
        const actions = document.getElementById(`btn-group_${currentRenderCardId}`);
        
        if (zone) {
            // Effet d'apparition stylisé de la photo
            zone.style.opacity = 0;
            
            setTimeout(() => {
                zone.innerHTML = `
                    <div class="final-image-container" style="box-shadow: 0 0 25px rgba(99, 102, 241, 0.3);">
                        <img src="${data.data}" alt="Publicité Visionary V4 générée" style="border-radius: var(--radius-md);">
                    </div>
                `;
                zone.style.transition = 'opacity 0.7s ease-in';
                zone.style.opacity = 1;
            }, 400); // 400ms delay rend la chose très théâtrale
        }

        if (actions) {
            actions.style.display = 'block';
            actions.innerHTML = `
                <a href="${data.data}" download="Visionary_Ads_${data.format}_${new Date().getTime()}.png" class="select-btn active" style="text-decoration:none; display:inline-block; font-size: 14px; padding: 12px 24px; font-weight:700;">
                    <span style="margin-right: 8px;">⬇</span> TÉLÉCHARGER LE RENDU
                </a>
            `;
        }

        triggerCleanup();
    }

    function triggerErrorState(data) {
        alert("Avertissement serveur : " + data.message);
        
        if (currentRenderCardId) {
            const elMsg = document.getElementById(`msg_${currentRenderCardId}`);
            const elBar = document.getElementById(`bar_${currentRenderCardId}`);
            if (elMsg && elBar) {
                 elMsg.textContent = "Génération interrompue.";
                 elMsg.style.color = "var(--danger-color)";
                 elBar.style.background = "var(--danger-color)";
            }
        }
        triggerCleanup();
    }

    function triggerCleanup() {
        console.log("Libération de la file d'attente d'images...");
        isGenerating = false;
        generateBtn.disabled = false;
        generateBtn.textContent = 'NOUVELLE GÉNÉRATION';
        currentRenderCardId = null;
    }

    // BOOT
    connectSocket();
});
