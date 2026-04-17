document.addEventListener('DOMContentLoaded', () => {
    
    // --- ÉLEMENTS DOM PRINCIPAUX --- //
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const imageGallery = document.getElementById('image-gallery');
    const imageCounter = document.getElementById('image-counter');
    
    const formatButtons = document.querySelectorAll('#format-selector .select-btn');
    const qualityButtons = document.querySelectorAll('#quality-selector .select-btn');
    
    // --- ÉTAT GLOBAL DE L'UI --- //
    // Cet objet stocke les valeurs configurées par l'utilisateur (utilisé à l'Etape 4)
    window.appUIState = {
        images: [],       // Tableau de string Base64 (max 9)
        format: 'post',   // Valeur par défaut
        quality: 'standard' // Valeur par défaut
    };

    const MAX_IMAGES_LIMIT = 9;

    // ================== LOGIQUE DES SÉLECTEURS ================== //
    
    function initSelector(buttonsGroup, stateKeyToUpdate) {
        buttonsGroup.forEach(btn => {
            btn.addEventListener('click', () => {
                // Éteint visuellement tous les boutons du groupe
                buttonsGroup.forEach(b => b.classList.remove('active'));
                // Allume celui cliqué
                btn.classList.add('active');
                // Met à jour la mémoire
                window.appUIState[stateKeyToUpdate] = btn.dataset.value;
            });
        });
    }

    // Activer les comportements
    initSelector(formatButtons, 'format');
    initSelector(qualityButtons, 'quality');

    // ================== LOGIQUE DRAG & DROP PHOTO ================== //

    // 1. Ouvre la fenêtre fichier si on clique sur la zone
    dropZone.addEventListener('click', () => fileInput.click());

    // 2. Comportement visuel du survol (Hover)
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    ['dragleave', 'dragend'].forEach(evt => {
        dropZone.addEventListener(evt, () => dropZone.classList.remove('dragover'));
    });

    // 3. Captage des fichiers lâchés
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            processImages(e.dataTransfer.files);
        }
    });

    // 4. Captage des fichiers sélectionnés via la fenêtre de parcours
    fileInput.addEventListener('change', (e) => {
        if (e.target.files && e.target.files.length > 0) {
            processImages(e.target.files);
        }
        // Purger l'input pour pouvoir resélectionner le même fichier si besoin
        fileInput.value = '';
    });

    function processImages(fileList) {
        // Obtenir uniquement les fichiers de type image
        const validImages = Array.from(fileList).filter(f => f.type.startsWith('image/'));
        
        if (validImages.length === 0) return;

        // Limiter de protection : On ne prend que ce qui rentre jusqu'à la limite des 9
        const remainingCapacity = MAX_IMAGES_LIMIT - window.appUIState.images.length;
        
        if (remainingCapacity <= 0) {
            alert('Vous avez déjà atteint la limite maximale de 9 photos pour le produit.');
            return;
        }

        const imagesToImport = validImages.slice(0, remainingCapacity);

        imagesToImport.forEach(file => {
            const reader = new FileReader();
            reader.onload = (readEvent) => {
                const base64Data = readEvent.target.result;
                window.appUIState.images.push(base64Data);
                refreshGalleryUI();
            };
            reader.readAsDataURL(file); // Encode l'image sur place
        });
    }

    // ================== METTRE A JOUR LA GALERIE VISUELLE ================== //
    
    function refreshGalleryUI() {
        // Vider la galerie
        imageGallery.innerHTML = '';
        
        // Boucler sur la liste d'images en mémoire
        window.appUIState.images.forEach((b64string, index) => {
            
            // Container de l'image
            const wrap = document.createElement('div');
            wrap.className = 'thumbnail-wrapper';
            
            // Image elle-même
            const imgEl = document.createElement('img');
            imgEl.src = b64string;
            
            // Bouton de suppression rouge
            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'remove-btn';
            deleteBtn.innerHTML = '×';
            deleteBtn.onclick = (e) => {
                e.stopPropagation(); // Evite de déclencher le drag&drop si on est dessus
                window.appUIState.images.splice(index, 1); // Enleve du tableau JS
                refreshGalleryUI(); // Recalcule la vue HTML
            };
            
            wrap.appendChild(imgEl);
            wrap.appendChild(deleteBtn);
            imageGallery.appendChild(wrap);
        });

        const currentTotal = window.appUIState.images.length;
        
        // Màj texte compteur
        imageCounter.textContent = `${currentTotal} / ${MAX_IMAGES_LIMIT}`;
        
        // Colorer le compteur en rouge si c'est plein
        if(currentTotal === MAX_IMAGES_LIMIT) {
            imageCounter.style.color = 'var(--danger-color)';
            dropZone.style.opacity = '0.3';
            dropZone.style.pointerEvents = 'none';
            document.querySelector('.drop-text').textContent = 'Limite maximale atteinte. Supprimez-en pour en rajouter.';
        } else {
            imageCounter.style.color = 'var(--accent-color)';
            dropZone.style.opacity = '1';
            dropZone.style.pointerEvents = 'auto';
            document.querySelector('.drop-text').textContent = 'Glissez-déposez vos photos de produits ici ou cliquez';
        }
    }
});
