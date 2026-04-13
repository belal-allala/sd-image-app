/**
 * SOCKET SERVICE - Gère la connexion WebSocket bidirectionnelle
 */
const SocketService = {
    socket: null,

    connect(onMessage, onOpen, onClose, onError) {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/generate`;
        
        this.socket = new WebSocket(wsUrl);

        this.socket.onopen = onOpen;
        this.socket.onclose = onClose;
        this.socket.onerror = onError;
        
        this.socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            onMessage(data);
        };
    },

    send(data) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify(data));
        }
    },

    close() {
        if (this.socket) this.socket.close();
    }
};

/**
 * UI MANAGER - Gère les éléments visuels et les barres de progression
 */
const UIManager = {
    promptInput: document.getElementById('prompt-input'),
    generateBtn: document.getElementById('generate-btn'),
    resultGrid: document.getElementById('result-grid'),

    initPlaceholders() {
        const formats = ["WhatsApp Story", "Instagram Post", "Facebook Cover", "Standard Photo"];
        this.resultGrid.innerHTML = '';
        
        formats.forEach((label) => {
            const card = document.createElement('div');
            card.className = 'format-card';
            // On utilise le label comme ID simplifié pour le ciblage JS
            const id = label.replace(/\s+/g, '-').toLowerCase();
            card.id = `card-${id}`;
            card.setAttribute('data-format', id); // Utilisé par le CSS pour l'aspect-ratio
            
            card.innerHTML = `
                <div class="image-box">
                    <img id="img-${id}" class="gen-image" src="" alt="${label}">
                    <div class="card-progress-overlay" id="overlay-${id}">
                        <div class="card-progress-fill" id="fill-${id}"></div>
                    </div>
                </div>
                <div class="card-info">
                    <div class="card-text">
                        <span class="card-label">${label}</span>
                        <span class="status-badge" id="badge-${id}">En attente</span>
                    </div>
                    <button id="dl-${id}" class="dl-btn" title="Télécharger">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                            <polyline points="7 10 12 15 17 10"></polyline>
                            <line x1="12" y1="15" x2="12" y2="3"></line>
                        </svg>
                    </button>
                </div>
            `;
            this.resultGrid.appendChild(card);
        });
    },

    updateProgress(label, value) {
        const id = label.replace(/\s+/g, '-').toLowerCase();
        const fill = document.getElementById(`fill-${id}`);
        const badge = document.getElementById(`badge-${id}`);
        
        if (fill) fill.style.width = `${value}%`;
        if (badge) badge.textContent = `Calcul : ${value}%`;
    },

    displayFinalImage(label, base64) {
        const id = label.replace(/\s+/g, '-').toLowerCase();
        const img = document.getElementById(`img-${id}`);
        const overlay = document.getElementById(`overlay-${id}`);
        const badge = document.getElementById(`badge-${id}`);
        const dlBtn = document.getElementById(`dl-${id}`);
        
        if (img) {
            img.src = base64;
            img.onload = () => {
                img.classList.add('loaded');
                if (overlay) overlay.classList.add('hidden');
                
                if (dlBtn) {
                    dlBtn.classList.add('visible');
                    dlBtn.onclick = () => {
                        const a = document.createElement('a');
                        a.href = base64;
                        const safePrompt = this.promptInput.value.replace(/[^a-z0-9]/gi, '_').substring(0, 15).toLowerCase();
                        a.download = `Visionary_${id}_${safePrompt}.png`;
                        a.click();
                    };
                }

                if (badge) {
                    badge.textContent = "Terminé";
                    badge.style.background = "rgba(139, 92, 246, 0.2)";
                    badge.style.color = "white";
                }
            };
        }
    },

    setLoading(isLoading) {
        this.generateBtn.disabled = isLoading;
        this.promptInput.disabled = isLoading;
        const btnText = document.querySelector('.btn-text');
        const loader = document.querySelector('.loader');

        if (isLoading) {
            btnText.textContent = "Session Active...";
            loader.classList.remove('hidden');
        } else {
            btnText.textContent = "Démarrer la Session";
            loader.classList.add('hidden');
        }
    }
};

/**
 * APP CONTROLLER - Orchestration globale
 */
const AppController = {
    init() {
        UIManager.generateBtn.addEventListener('click', () => this.handleStart());
        UIManager.promptInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') this.handleStart();
        });
    },

    handleStart() {
        const prompt = UIManager.promptInput.value.trim();
        if (!prompt) return;

        UIManager.setLoading(true);
        UIManager.initPlaceholders();

        // Connexion WebSocket
        SocketService.connect(
            (data) => this.handleServerMessage(data),
            () => {
                console.log("[*] Socket ouvert. Envoi du prompt.");
                SocketService.send({ prompt: prompt });
            },
            () => {
                console.log("[*] Socket fermé.");
                UIManager.setLoading(false);
            },
            (err) => {
                alert("Erreur WebSocket. Vérifiez le serveur.");
                UIManager.setLoading(false);
            }
        );
    },

    handleServerMessage(data) {
        switch (data.type) {
            case 'progress':
                UIManager.updateProgress(data.label, data.value);
                break;
            case 'image':
                UIManager.displayFinalImage(data.label, data.base64);
                break;
            case 'complete':
                console.log("[+] Toute la session est terminée.");
                SocketService.close();
                break;
            case 'error':
                alert("Erreur Serveur: " + data.message);
                SocketService.close();
                break;
        }
    }
};

// Start App
AppController.init();
