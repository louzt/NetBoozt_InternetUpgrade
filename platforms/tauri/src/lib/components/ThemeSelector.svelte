<!--
    ThemeSelector.svelte - Selector de temas y wallpapers
    By LOUST
-->
<script lang="ts">
    import { themeState, currentTheme, setTheme, setWallpaper, getAvailableThemes, type Theme } from '$lib/stores/themeStore';
    import Icon from './Icon.svelte';
    
    // Estado local
    let showWallpaperModal = false;
    let wallpaperUrl = '';
    let previewTheme: Theme | null = null;
    
    // Temas disponibles
    $: themes = getAvailableThemes();
    $: activeTheme = $currentTheme;
    $: customWallpaper = $themeState.customWallpaper;
    
    function selectTheme(theme: Theme) {
        setTheme(theme.id);
    }
    
    function openWallpaperModal() {
        wallpaperUrl = customWallpaper || '';
        showWallpaperModal = true;
    }
    
    function closeWallpaperModal() {
        showWallpaperModal = false;
        previewTheme = null;
    }
    
    function applyWallpaper() {
        if (wallpaperUrl.trim()) {
            setWallpaper(wallpaperUrl.trim());
        } else {
            setWallpaper(null);
        }
        closeWallpaperModal();
    }
    
    function clearWallpaper() {
        setWallpaper(null);
        wallpaperUrl = '';
    }
    
    function handleFileInput(event: Event) {
        const target = event.target as HTMLInputElement;
        const file = target.files?.[0];
        
        if (file) {
            // Leer archivo como data URL
            const reader = new FileReader();
            reader.onload = (e) => {
                wallpaperUrl = e.target?.result as string;
            };
            reader.readAsDataURL(file);
        }
    }
    
    // Preview de colores
    function getColorPreview(theme: Theme): string[] {
        const c = theme.colors;
        return [c.primary, c.background, c.card, c.success];
    }
</script>

<div class="theme-selector">
    <div class="section-header">
        <Icon name="layers" size={18} />
        <h3>Apariencia</h3>
    </div>
    
    <!-- Selector de Tema -->
    <div class="themes-grid">
        {#each themes as theme (theme.id)}
            <button
                class="theme-card"
                class:active={activeTheme.id === theme.id}
                on:click={() => selectTheme(theme)}
                style="--preview-bg: {theme.background.type === 'solid' ? theme.background.value : theme.colors.background}"
            >
                <div class="theme-preview">
                    <div class="preview-bg" style="background: {theme.background.type === 'solid' ? theme.background.value : theme.background.value}"></div>
                    <div class="preview-colors">
                        {#each getColorPreview(theme) as color}
                            <span class="color-dot" style="background: {color}"></span>
                        {/each}
                    </div>
                </div>
                <div class="theme-info">
                    <span class="theme-name">{theme.name}</span>
                    <span class="theme-type">{theme.type === 'dark' ? '🌙' : '☀️'}</span>
                </div>
                {#if activeTheme.id === theme.id}
                    <span class="active-indicator">
                        <Icon name="check" size={12} />
                    </span>
                {/if}
            </button>
        {/each}
    </div>
    
    <!-- Wallpaper Personalizado -->
    <div class="wallpaper-section">
        <div class="wallpaper-header">
            <Icon name="image" size={16} />
            <span>Fondo Personalizado</span>
        </div>
        
        {#if customWallpaper}
            <div class="current-wallpaper">
                <div class="wallpaper-preview" style="background-image: url('{customWallpaper}')"></div>
                <div class="wallpaper-actions">
                    <button class="btn btn-sm" on:click={openWallpaperModal}>
                        <Icon name="edit" size={14} />
                        Cambiar
                    </button>
                    <button class="btn btn-sm btn-danger" on:click={clearWallpaper}>
                        <Icon name="x" size={14} />
                        Quitar
                    </button>
                </div>
            </div>
        {:else}
            <button class="add-wallpaper-btn" on:click={openWallpaperModal}>
                <Icon name="plus-circle" size={20} />
                <span>Agregar fondo</span>
            </button>
        {/if}
    </div>
    
    <!-- Efectos -->
    <div class="effects-section">
        <div class="effect-row">
            <span>Glassmorphism</span>
            <span class="effect-value">{activeTheme.effects.glassmorphism ? 'Activado' : 'Desactivado'}</span>
        </div>
        <div class="effect-row">
            <span>Blur</span>
            <span class="effect-value">{activeTheme.effects.blur}px</span>
        </div>
    </div>
</div>

<!-- Modal de Wallpaper -->
{#if showWallpaperModal}
    <!-- svelte-ignore a11y-click-events-have-key-events a11y-no-static-element-interactions -->
    <div class="modal-backdrop" on:click={closeWallpaperModal}>
        <!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
        <div class="modal" on:click|stopPropagation on:keydown={(e) => e.key === 'Escape' && closeWallpaperModal()} role="dialog" aria-modal="true">
            <div class="modal-header">
                <h4>Fondo Personalizado</h4>
                <button class="close-btn" on:click={closeWallpaperModal}>
                    <Icon name="x" size={18} />
                </button>
            </div>
            
            <div class="modal-body">
                <div class="input-group">
                    <label for="wallpaper-url">URL de imagen</label>
                    <input
                        type="text"
                        id="wallpaper-url"
                        bind:value={wallpaperUrl}
                        placeholder="https://ejemplo.com/imagen.jpg"
                    />
                </div>
                
                <div class="divider">o</div>
                
                <div class="file-upload">
                    <label class="upload-btn">
                        <Icon name="upload" size={20} />
                        <span>Subir imagen local</span>
                        <input type="file" accept="image/*" on:change={handleFileInput} />
                    </label>
                    <p class="hint">JPG, PNG, WebP, GIF • Max 5MB</p>
                </div>
                
                {#if wallpaperUrl}
                    <div class="preview-section">
                        <span class="preview-label">Vista previa</span>
                        <div class="image-preview" style="background-image: url('{wallpaperUrl}')"></div>
                    </div>
                {/if}
            </div>
            
            <div class="modal-footer">
                <button class="btn btn-secondary" on:click={closeWallpaperModal}>Cancelar</button>
                <button class="btn btn-primary" on:click={applyWallpaper}>Aplicar</button>
            </div>
        </div>
    </div>
{/if}

<style>
    .theme-selector {
        display: flex;
        flex-direction: column;
        gap: 1.25rem;
    }
    
    .section-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: var(--primary, #00d4aa);
    }
    
    .section-header h3 {
        margin: 0;
        font-size: 1rem;
        font-weight: 600;
        color: var(--text-primary, #fff);
    }
    
    /* Themes Grid */
    .themes-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
        gap: 0.75rem;
    }
    
    .theme-card {
        position: relative;
        background: rgba(255, 255, 255, 0.03);
        border: 2px solid transparent;
        border-radius: 12px;
        padding: 0.75rem;
        cursor: pointer;
        transition: all 0.2s;
        text-align: left;
    }
    
    .theme-card:hover {
        background: rgba(255, 255, 255, 0.06);
        border-color: rgba(255, 255, 255, 0.1);
    }
    
    .theme-card.active {
        border-color: var(--primary, #00d4aa);
        background: rgba(0, 212, 170, 0.1);
    }
    
    .theme-preview {
        position: relative;
        height: 60px;
        border-radius: 8px;
        overflow: hidden;
        margin-bottom: 0.5rem;
    }
    
    .preview-bg {
        position: absolute;
        inset: 0;
    }
    
    .preview-colors {
        position: absolute;
        bottom: 6px;
        left: 6px;
        display: flex;
        gap: 4px;
    }
    
    .color-dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .theme-info {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .theme-name {
        font-size: 0.8rem;
        font-weight: 500;
        color: var(--text-primary, #fff);
    }
    
    .theme-type {
        font-size: 0.75rem;
    }
    
    .active-indicator {
        position: absolute;
        top: 8px;
        right: 8px;
        width: 20px;
        height: 20px;
        background: var(--primary, #00d4aa);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #000;
    }
    
    /* Wallpaper Section */
    .wallpaper-section {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 12px;
        padding: 1rem;
    }
    
    .wallpaper-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: var(--text-secondary, #a0a0a0);
        font-size: 0.8rem;
        margin-bottom: 0.75rem;
    }
    
    .add-wallpaper-btn {
        width: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        padding: 1rem;
        background: rgba(0, 212, 170, 0.1);
        border: 2px dashed rgba(0, 212, 170, 0.3);
        border-radius: 8px;
        color: var(--primary, #00d4aa);
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .add-wallpaper-btn:hover {
        background: rgba(0, 212, 170, 0.15);
        border-color: var(--primary, #00d4aa);
    }
    
    .current-wallpaper {
        display: flex;
        gap: 1rem;
        align-items: center;
    }
    
    .wallpaper-preview {
        width: 80px;
        height: 50px;
        border-radius: 8px;
        background-size: cover;
        background-position: center;
    }
    
    .wallpaper-actions {
        display: flex;
        gap: 0.5rem;
    }
    
    /* Effects Section */
    .effects-section {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 12px;
        padding: 1rem;
    }
    
    .effect-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.5rem 0;
        font-size: 0.8rem;
    }
    
    .effect-row:not(:last-child) {
        border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    }
    
    .effect-value {
        color: var(--text-muted, #666);
    }
    
    /* Buttons */
    .btn {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.5rem 0.75rem;
        border-radius: 6px;
        font-size: 0.75rem;
        cursor: pointer;
        border: none;
        transition: all 0.15s;
    }
    
    .btn-sm {
        padding: 0.35rem 0.6rem;
        font-size: 0.7rem;
    }
    
    .btn-primary {
        background: var(--primary, #00d4aa);
        color: #000;
    }
    
    .btn-secondary {
        background: rgba(255, 255, 255, 0.1);
        color: var(--text-secondary, #a0a0a0);
    }
    
    .btn-danger {
        background: rgba(255, 107, 107, 0.15);
        color: #ff6b6b;
    }
    
    /* Modal */
    .modal-backdrop {
        position: fixed;
        inset: 0;
        background: rgba(0, 0, 0, 0.7);
        backdrop-filter: blur(4px);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
    }
    
    .modal {
        background: rgba(26, 26, 26, 0.95);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        width: 90%;
        max-width: 420px;
        overflow: hidden;
    }
    
    .modal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 1.25rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    .modal-header h4 {
        margin: 0;
        font-size: 1rem;
        color: var(--text-primary, #fff);
    }
    
    .close-btn {
        background: transparent;
        border: none;
        color: var(--text-muted, #666);
        cursor: pointer;
        padding: 0.25rem;
    }
    
    .modal-body {
        padding: 1.25rem;
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }
    
    .input-group {
        display: flex;
        flex-direction: column;
        gap: 0.35rem;
    }
    
    .input-group label {
        font-size: 0.75rem;
        color: var(--text-secondary, #a0a0a0);
    }
    
    .input-group input {
        padding: 0.625rem 0.75rem;
        background: rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        color: var(--text-primary, #fff);
        font-size: 0.85rem;
    }
    
    .divider {
        text-align: center;
        color: var(--text-muted, #666);
        font-size: 0.75rem;
        position: relative;
    }
    
    .divider::before,
    .divider::after {
        content: '';
        position: absolute;
        top: 50%;
        width: 40%;
        height: 1px;
        background: rgba(255, 255, 255, 0.08);
    }
    
    .divider::before { left: 0; }
    .divider::after { right: 0; }
    
    .file-upload {
        text-align: center;
    }
    
    .upload-btn {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.75rem 1.25rem;
        background: rgba(255, 255, 255, 0.05);
        border: 2px dashed rgba(255, 255, 255, 0.15);
        border-radius: 8px;
        color: var(--text-secondary, #a0a0a0);
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .upload-btn:hover {
        border-color: var(--primary, #00d4aa);
        color: var(--primary, #00d4aa);
    }
    
    .upload-btn input {
        display: none;
    }
    
    .hint {
        font-size: 0.7rem;
        color: var(--text-muted, #666);
        margin-top: 0.5rem;
    }
    
    .preview-section {
        margin-top: 0.5rem;
    }
    
    .preview-label {
        display: block;
        font-size: 0.75rem;
        color: var(--text-secondary, #a0a0a0);
        margin-bottom: 0.5rem;
    }
    
    .image-preview {
        width: 100%;
        height: 120px;
        border-radius: 8px;
        background-size: cover;
        background-position: center;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .modal-footer {
        display: flex;
        justify-content: flex-end;
        gap: 0.75rem;
        padding: 1rem 1.25rem;
        border-top: 1px solid rgba(255, 255, 255, 0.08);
    }
</style>
