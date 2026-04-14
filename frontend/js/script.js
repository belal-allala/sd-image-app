document.addEventListener('DOMContentLoaded', () => {
    // UI Elements with safely fallback checks
    const uploadArea = document.getElementById('upload-area');
    const imageUpload = document.getElementById('image-upload');
    const imagePreview = document.getElementById('image-preview');
    const uploadText = document.getElementById('upload-text');
    const strengthSlider = document.getElementById('strength');
    const strengthVal = document.getElementById('strength-val');
    const generateBtn = document.getElementById('generate-btn');
    const promptInput = document.getElementById('prompt');
    const resultsGrid = document.getElementById('results-grid');
    const emptyState = document.getElementById('empty-state');
    const wsStatusDot = document.getElementById('ws-status');
    const wsStatusText = document.getElementById('ws-text');

    // Make sure we break gracefully if something is missing
    if (!generateBtn) {
        console.error("Critical UI component missing: 'generate-btn' not found in the DOM. Ensure index.html is loaded correctly.");
        return;
    }

    let base64Image = null;
    let ws = null;

    // Connect WebSocket
    function connectWebSocket() {
        if (!wsStatusDot || !wsStatusText) return;

        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.host || 'localhost:8000'; 
        const wsUrl = `${protocol}//${host}/ws/generate`;
        
        ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            wsStatusDot.classList.remove('disconnected');
            wsStatusDot.classList.add('connected');
            wsStatusText.textContent = 'CONNECTÉ';
            if (generateBtn) generateBtn.disabled = false;
        };

        ws.onclose = () => {
            wsStatusDot.classList.remove('connected');
            wsStatusDot.classList.add('disconnected');
            wsStatusText.textContent = 'DÉCONNECTÉ';
            if (generateBtn) generateBtn.disabled = true;
            setTimeout(connectWebSocket, 3000); // Auto reconnect
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            handleWsMessage(data);
        };
    }

    // Handle WebSocket Messages
    function handleWsMessage(data) {
        if (data.type === 'progress') {
            const cardId = `card-${data.format.replace(/\s+/g, '-')}`;
            const progressBar = document.querySelector(`#${cardId} .progress-bar`);
            const progressText = document.querySelector(`#${cardId} .progress-text`);
            
            if (progressBar && progressText) {
                progressBar.style.width = `${data.progress}%`;
                progressText.textContent = `${data.progress}% (${data.step}/${data.total_steps})`;
            }
        } 
        else if (data.type === 'image') {
            const cardId = `card-${data.format.replace(/\s+/g, '-')}`;
            const card = document.getElementById(cardId);
            if (card) {
                const img = card.querySelector('.result-image');
                const placeholder = card.querySelector('.placeholder');
                const progressContainer = card.querySelector('.progress-container');
                const progressText = card.querySelector('.progress-text');
                const downloadBtn = card.querySelector('.download-btn');

                img.src = data.image;
                img.onload = () => {
                    if (placeholder) placeholder.style.display = 'none';
                    img.classList.add('loaded');
                };

                if (progressContainer) progressContainer.style.display = 'none';
                if (progressText) progressText.textContent = 'GÉNÉRATION TERMINÉE !';
                
                if (downloadBtn) {
                    downloadBtn.href = data.image;
                    downloadBtn.download = `Visionary_${data.format.replace(/\s+/g, '_')}.png`;
                    downloadBtn.style.display = 'block';
                }
            }
        }
        else if (data.type === 'complete') {
            if (generateBtn) {
                generateBtn.disabled = false;
                generateBtn.classList.remove('generating');
                generateBtn.textContent = 'GÉNÉRER';
            }
        }
        else if (data.type === 'error') {
            alert('Erreur du serveur: ' + data.message);
            if (generateBtn) {
                generateBtn.disabled = false;
                generateBtn.classList.remove('generating');
                generateBtn.textContent = 'GÉNÉRER';
            }
        }
    }

    // Upload & Drag-n-Drop Logic
    if (uploadArea && imageUpload) {
        uploadArea.addEventListener('click', () => imageUpload.click());

        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                handleFile(e.dataTransfer.files[0]);
            }
        });

        imageUpload.addEventListener('change', (e) => {
            if (e.target.files && e.target.files[0]) {
                handleFile(e.target.files[0]);
            }
        });
    }

    function handleFile(file) {
        if (!file.type.startsWith('image/')) {
            alert("Seules les images sont autorisées !");
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            base64Image = e.target.result;
            if (imagePreview) {
                imagePreview.src = base64Image;
                imagePreview.style.display = 'block';
            }
            if (uploadText) {
                uploadText.style.display = 'none';
            }
        };
        reader.readAsDataURL(file);
    }

    // Strength Slider
    if (strengthSlider && strengthVal) {
        strengthSlider.addEventListener('input', (e) => {
            strengthVal.textContent = e.target.value;
        });
    }

    // Generate Action
    if (generateBtn) {
        generateBtn.addEventListener('click', () => {
            const prompt = promptInput ? promptInput.value.trim() : "";
            if (!prompt) {
                alert("Veuillez entrer un prompt magique !");
                return;
            }

            const checkboxes = document.querySelectorAll('.format-checkbox input:checked');
            if (checkboxes.length === 0) {
                alert("Veuillez sélectionner au moins un format de sortie.");
                return;
            }

            const formats = Array.from(checkboxes).map(cb => ({
                name: cb.dataset.name,
                width: parseInt(cb.dataset.width),
                height: parseInt(cb.dataset.height)
            }));

            const requestData = {
                prompt: prompt,
                init_image: base64Image,
                formats: formats,
                strength: strengthSlider ? parseFloat(strengthSlider.value) : 0.75
            };

            // Prepare UI
            if (emptyState) emptyState.style.display = 'none';
            generateBtn.disabled = true;
            generateBtn.classList.add('generating');
            generateBtn.textContent = 'TRAITEMENT IA...';
            
            // Setup Grid
            if (resultsGrid) {
                resultsGrid.innerHTML = '';
                formats.forEach(f => {
                    const aspect = f.width / f.height;
                    const cardId = `card-${f.name.replace(/\s+/g, '-')}`;
                    
                    const cardHTML = `
                        <div class="result-card" id="${cardId}">
                            <div class="card-header">
                                <span>${f.name}</span>
                                <span style="opacity: 0.6;">${f.width}x${f.height}</span>
                            </div>
                            <div class="image-container" style="aspect-ratio: ${aspect};">
                                <div class="placeholder"></div>
                                <img class="result-image" alt="${f.name}">
                            </div>
                            <div style="margin-top:auto;">
                                <div class="progress-text">Connexion neuronale...</div>
                                <div class="progress-container">
                                    <div class="progress-bar"></div>
                                </div>
                            </div>
                            <a class="download-btn">TÉLÉCHARGER LA CRÉATION</a>
                        </div>
                    `;
                    resultsGrid.insertAdjacentHTML('beforeend', cardHTML);
                });
            }

            // Send to WebSocket
            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify(requestData));
            } else {
                alert("Système hors-ligne. Serveur WebSocket introuvable.");
                generateBtn.disabled = false;
                generateBtn.classList.remove('generating');
                generateBtn.textContent = 'GÉNÉRER';
            }
        });
    }

    // Initialize Connection on Load
    connectWebSocket();
});
