/**
 * Positive Vocabulary Gallery - JavaScript Application
 * 
 * Features:
 * - Load and parse metadata.json
 * - Fisher-Yates shuffle on page load
 * - Responsive 4-column grid
 * - Full-screen slideshow with autoplay
 * - Search/filter by vocabulary words
 * - Keyboard navigation
 * - Touch swipe support
 */

// =========================================
// Configuration
// =========================================
const CONFIG = {
    metadataFile: 'metadata.json',
    mediaFolder: 'positivevocab',
    defaultAutoplaySpeed: 3000,
    maxWordsToShow: 5,
    debounceDelay: 300
};

// =========================================
// State Management
// =========================================
const state = {
    allItems: [],
    filteredItems: [],
    currentSlideIndex: 0,
    isAutoplayActive: false,
    autoplayInterval: null,
    autoplaySpeed: CONFIG.defaultAutoplaySpeed,
    searchQuery: ''
};

// =========================================
// DOM Elements
// =========================================
const elements = {
    gallery: document.getElementById('gallery'),
    loadingState: document.getElementById('loadingState'),
    emptyState: document.getElementById('emptyState'),
    searchInput: document.getElementById('searchInput'),
    slideshowBtn: document.getElementById('slideshowBtn'),
    shuffleBtn: document.getElementById('shuffleBtn'),

    // Stats
    totalCount: document.getElementById('totalCount'),
    imageCount: document.getElementById('imageCount'),
    videoCount: document.getElementById('videoCount'),
    visibleCount: document.getElementById('visibleCount'),
    generatedDate: document.getElementById('generatedDate'),

    // Modal
    slideshowModal: document.getElementById('slideshowModal'),
    closeSlideshow: document.getElementById('closeSlideshow'),
    prevSlide: document.getElementById('prevSlide'),
    nextSlide: document.getElementById('nextSlide'),
    slideshowImage: document.getElementById('slideshowImage'),
    slideshowVideo: document.getElementById('slideshowVideo'),
    slideshowVideoSource: document.getElementById('slideshowVideoSource'),
    currentSlide: document.getElementById('currentSlide'),
    totalSlides: document.getElementById('totalSlides'),
    slideshowWords: document.getElementById('slideshowWords'),
    autoplayBtn: document.getElementById('autoplayBtn'),
    autoplayIcon: document.getElementById('autoplayIcon'),
    autoplayText: document.getElementById('autoplayText'),
    speedSelect: document.getElementById('speedSelect')
};

// =========================================
// Utility Functions
// =========================================

/**
 * Fisher-Yates shuffle algorithm
 */
function shuffle(array) {
    const shuffled = [...array];
    for (let i = shuffled.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled;
}

/**
 * Debounce function for search
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Format date for display
 */
function formatDate(isoString) {
    try {
        const date = new Date(isoString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    } catch {
        return '-';
    }
}

/**
 * Get media source URL
 */
function getMediaUrl(filename) {
    return `${CONFIG.mediaFolder}/${filename}`;
}

// =========================================
// Gallery Rendering
// =========================================

/**
 * Create a gallery item element
 */
function createGalleryItem(item, index) {
    const div = document.createElement('div');
    div.className = 'gallery-item';
    div.dataset.index = index;

    const isVideo = item.type === 'video';
    const mediaUrl = getMediaUrl(item.filename);

    // Create appropriate media element
    if (isVideo) {
        div.innerHTML = `
            <video src="${mediaUrl}" preload="metadata" muted></video>
            <span class="media-badge video">Video</span>
            <div class="video-indicator">▶</div>
        `;
    } else {
        div.innerHTML = `
            <img src="${mediaUrl}" alt="${item.filename}" loading="lazy">
            ${item.format === 'gif' ? '<span class="media-badge">GIF</span>' : ''}
        `;
    }

    // Add words overlay if available
    if (item.words && item.words.length > 0) {
        const wordsHtml = item.words
            .slice(0, CONFIG.maxWordsToShow)
            .map(word => `<span class="word-tag">${word}</span>`)
            .join('');
        div.innerHTML += `<div class="item-words">${wordsHtml}</div>`;
    }

    // Click handler
    div.addEventListener('click', () => openSlideshow(index));

    return div;
}

/**
 * Render gallery grid
 */
function renderGallery() {
    elements.gallery.innerHTML = '';

    if (state.filteredItems.length === 0) {
        elements.emptyState.classList.remove('hidden');
        elements.visibleCount.textContent = '0';
        return;
    }

    elements.emptyState.classList.add('hidden');

    state.filteredItems.forEach((item, index) => {
        const element = createGalleryItem(item, index);
        elements.gallery.appendChild(element);
    });

    elements.visibleCount.textContent = state.filteredItems.length;
}

/**
 * Update stats display
 */
function updateStats(metadata) {
    elements.totalCount.textContent = metadata.totalFiles || 0;
    elements.imageCount.textContent = metadata.imageCount || 0;
    elements.videoCount.textContent = metadata.videoCount || 0;
    elements.visibleCount.textContent = state.filteredItems.length;
    elements.generatedDate.textContent = formatDate(metadata.generated);
}

// =========================================
// Search & Filter
// =========================================

/**
 * Filter items based on search query
 */
function filterItems() {
    const query = state.searchQuery.toLowerCase().trim();

    if (!query) {
        state.filteredItems = [...state.allItems];
    } else {
        state.filteredItems = state.allItems.filter(item => {
            // Search in filename
            if (item.filename.toLowerCase().includes(query)) return true;

            // Search in extracted text
            if (item.extractedText && item.extractedText.toLowerCase().includes(query)) return true;

            // Search in words array
            if (item.words && item.words.some(word => word.toLowerCase().includes(query))) return true;

            // Search in synonyms array
            if (item.synonyms && item.synonyms.some(syn => syn.toLowerCase().includes(query))) return true;

            return false;
        });
    }

    renderGallery();
}

/**
 * Handle search input
 */
const handleSearch = debounce((event) => {
    state.searchQuery = event.target.value;
    filterItems();
}, CONFIG.debounceDelay);

// =========================================
// Slideshow
// =========================================

/**
 * Open slideshow at specific index
 */
function openSlideshow(index) {
    state.currentSlideIndex = index;
    elements.slideshowModal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
    updateSlideContent();
    elements.totalSlides.textContent = state.filteredItems.length;
}

/**
 * Close slideshow
 */
function closeSlideshow() {
    elements.slideshowModal.classList.add('hidden');
    document.body.style.overflow = '';
    stopAutoplay();

    // Pause video if playing
    elements.slideshowVideo.pause();
}

/**
 * Navigate to next slide
 */
function nextSlide() {
    state.currentSlideIndex = (state.currentSlideIndex + 1) % state.filteredItems.length;
    updateSlideContent();
}

/**
 * Navigate to previous slide
 */
function prevSlide() {
    state.currentSlideIndex = (state.currentSlideIndex - 1 + state.filteredItems.length) % state.filteredItems.length;
    updateSlideContent();
}

/**
 * Update slide content
 */
function updateSlideContent() {
    const item = state.filteredItems[state.currentSlideIndex];
    if (!item) return;

    const mediaUrl = getMediaUrl(item.filename);
    const isVideo = item.type === 'video';

    // Show/hide appropriate media element
    if (isVideo) {
        elements.slideshowImage.classList.add('hidden');
        elements.slideshowVideo.classList.remove('hidden');
        elements.slideshowVideoSource.src = mediaUrl;
        elements.slideshowVideo.load();
    } else {
        elements.slideshowVideo.classList.add('hidden');
        elements.slideshowVideo.pause();
        elements.slideshowImage.classList.remove('hidden');
        elements.slideshowImage.src = mediaUrl;
        elements.slideshowImage.alt = item.filename;
    }

    // Update counter
    elements.currentSlide.textContent = state.currentSlideIndex + 1;

    // Update words
    elements.slideshowWords.innerHTML = '';
    if (item.words && item.words.length > 0) {
        item.words.slice(0, 10).forEach(word => {
            const tag = document.createElement('span');
            tag.className = 'word-tag';
            tag.textContent = word;
            elements.slideshowWords.appendChild(tag);
        });
    }
}

/**
 * Toggle autoplay
 */
function toggleAutoplay() {
    if (state.isAutoplayActive) {
        stopAutoplay();
    } else {
        startAutoplay();
    }
}

/**
 * Start autoplay
 */
function startAutoplay() {
    state.isAutoplayActive = true;
    elements.autoplayBtn.classList.add('active');
    elements.autoplayIcon.textContent = '⏸';
    elements.autoplayText.textContent = 'Stop';

    state.autoplayInterval = setInterval(() => {
        nextSlide();
    }, state.autoplaySpeed);
}

/**
 * Stop autoplay
 */
function stopAutoplay() {
    state.isAutoplayActive = false;
    elements.autoplayBtn.classList.remove('active');
    elements.autoplayIcon.textContent = '▶';
    elements.autoplayText.textContent = 'Auto';

    if (state.autoplayInterval) {
        clearInterval(state.autoplayInterval);
        state.autoplayInterval = null;
    }
}

/**
 * Handle speed change
 */
function handleSpeedChange(event) {
    state.autoplaySpeed = parseInt(event.target.value, 10);

    // Restart autoplay with new speed if active
    if (state.isAutoplayActive) {
        stopAutoplay();
        startAutoplay();
    }
}

// =========================================
// Shuffle
// =========================================

/**
 * Shuffle and re-render gallery
 */
function shuffleGallery() {
    state.allItems = shuffle(state.allItems);
    filterItems(); // This will update filteredItems and re-render

    // Add visual feedback
    elements.shuffleBtn.style.transform = 'rotate(360deg)';
    setTimeout(() => {
        elements.shuffleBtn.style.transform = '';
    }, 300);
}

// =========================================
// Keyboard Navigation
// =========================================

function handleKeydown(event) {
    // Only handle when modal is open
    if (elements.slideshowModal.classList.contains('hidden')) return;

    switch (event.key) {
        case 'ArrowLeft':
            prevSlide();
            break;
        case 'ArrowRight':
            nextSlide();
            break;
        case 'Escape':
            closeSlideshow();
            break;
        case ' ':
            event.preventDefault();
            toggleAutoplay();
            break;
    }
}

// =========================================
// Touch Swipe Support
// =========================================

let touchStartX = 0;
let touchEndX = 0;

function handleTouchStart(event) {
    touchStartX = event.changedTouches[0].screenX;
}

function handleTouchEnd(event) {
    touchEndX = event.changedTouches[0].screenX;
    handleSwipe();
}

function handleSwipe() {
    const swipeThreshold = 50;
    const diff = touchStartX - touchEndX;

    if (Math.abs(diff) < swipeThreshold) return;

    if (diff > 0) {
        nextSlide();
    } else {
        prevSlide();
    }
}

// =========================================
// Initialization
// =========================================

/**
 * Load metadata and initialize gallery
 */
async function init() {
    try {
        // Fetch metadata
        const response = await fetch(CONFIG.metadataFile);

        if (!response.ok) {
            throw new Error(`Failed to load metadata: ${response.status}`);
        }

        const metadata = await response.json();

        // Shuffle items on load
        state.allItems = shuffle(metadata.files || []);
        state.filteredItems = [...state.allItems];

        // Update stats
        updateStats(metadata);

        // Hide loading, render gallery
        elements.loadingState.classList.add('hidden');
        renderGallery();

        console.log(`Gallery loaded: ${state.allItems.length} items`);

    } catch (error) {
        console.error('Failed to initialize gallery:', error);
        elements.loadingState.innerHTML = `
            <div class="empty-icon">⚠️</div>
            <h2>Failed to load gallery</h2>
            <p>Please run the preprocessing script first:</p>
            <code style="display: block; margin-top: 1rem; padding: 1rem; background: var(--bg-tertiary); border-radius: 8px;">
                python preprocess.py
            </code>
        `;
    }
}

/**
 * Set up event listeners
 */
function setupEventListeners() {
    // Search
    elements.searchInput.addEventListener('input', handleSearch);

    // Buttons
    elements.slideshowBtn.addEventListener('click', () => openSlideshow(0));
    elements.shuffleBtn.addEventListener('click', shuffleGallery);

    // Modal controls
    elements.closeSlideshow.addEventListener('click', closeSlideshow);
    elements.prevSlide.addEventListener('click', prevSlide);
    elements.nextSlide.addEventListener('click', nextSlide);
    elements.autoplayBtn.addEventListener('click', toggleAutoplay);
    elements.speedSelect.addEventListener('change', handleSpeedChange);

    // Close modal on backdrop click
    elements.slideshowModal.querySelector('.modal-backdrop').addEventListener('click', closeSlideshow);

    // Keyboard navigation
    document.addEventListener('keydown', handleKeydown);

    // Touch swipe
    elements.slideshowModal.addEventListener('touchstart', handleTouchStart);
    elements.slideshowModal.addEventListener('touchend', handleTouchEnd);
}

// =========================================
// Start Application
// =========================================
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    init();
});
