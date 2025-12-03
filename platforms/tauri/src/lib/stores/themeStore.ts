/**
 * themeStore.ts - Sistema de temas y wallpapers para NetBoozt
 * Maneja la persistencia de preferencias visuales
 * By LOUST (www.loust.pro)
 */

import { writable, derived, get } from 'svelte/store';
import { browser } from '$app/environment';

// Tipos
export interface ThemeColors {
    primary: string;
    background: string;
    card: string;
    border: string;
    text: string;
    textSecondary: string;
    textMuted: string;
    success: string;
    warning: string;
    error: string;
}

export interface ThemeEffects {
    glassmorphism: boolean;
    blur: number;
    cardOpacity: number;
}

export interface Theme {
    id: string;
    name: string;
    version: string;
    author: string;
    type: 'dark' | 'light';
    background: {
        type: 'solid' | 'gradient' | 'image';
        value: string;
    };
    colors: ThemeColors;
    effects: ThemeEffects;
}

export interface ThemeState {
    currentThemeId: string;
    customWallpaper: string | null;
    themes: Theme[];
}

// Temas por defecto
const DEFAULT_THEMES: Theme[] = [
    {
        id: 'default-dark',
        name: 'NetBoozt Dark',
        version: '1.0.0',
        author: 'LOUST',
        type: 'dark',
        background: {
            type: 'solid',
            value: '#0a0a0a'
        },
        colors: {
            primary: '#00d4aa',
            background: '#0a0a0a',
            card: '#1a1a1a',
            border: '#2d2d2d',
            text: '#ffffff',
            textSecondary: '#a0a0a0',
            textMuted: '#666666',
            success: '#00ff88',
            warning: '#fdcb6e',
            error: '#ff6b6b'
        },
        effects: {
            glassmorphism: true,
            blur: 12,
            cardOpacity: 0.7
        }
    },
    {
        id: 'matrix',
        name: 'Matrix',
        version: '1.0.0',
        author: 'LOUST',
        type: 'dark',
        background: {
            type: 'gradient',
            value: 'linear-gradient(180deg, #000000 0%, #001a0d 50%, #000000 100%)'
        },
        colors: {
            primary: '#00ff41',
            background: '#000000',
            card: '#0a1a0d',
            border: '#003d1a',
            text: '#00ff41',
            textSecondary: '#00cc33',
            textMuted: '#006622',
            success: '#00ff41',
            warning: '#99ff00',
            error: '#ff0040'
        },
        effects: {
            glassmorphism: true,
            blur: 16,
            cardOpacity: 0.5
        }
    },
    {
        id: 'cyber',
        name: 'Cyberpunk',
        version: '1.0.0',
        author: 'LOUST',
        type: 'dark',
        background: {
            type: 'gradient',
            value: 'linear-gradient(135deg, #0a0015 0%, #1a0030 50%, #0f0020 100%)'
        },
        colors: {
            primary: '#ff00ff',
            background: '#0a0015',
            card: '#1a0030',
            border: '#3d0066',
            text: '#ffffff',
            textSecondary: '#cc99ff',
            textMuted: '#9966cc',
            success: '#00ffff',
            warning: '#ffff00',
            error: '#ff0066'
        },
        effects: {
            glassmorphism: true,
            blur: 20,
            cardOpacity: 0.4
        }
    },
    {
        id: 'minimal',
        name: 'Minimal',
        version: '1.0.0',
        author: 'LOUST',
        type: 'dark',
        background: {
            type: 'solid',
            value: '#121212'
        },
        colors: {
            primary: '#ffffff',
            background: '#121212',
            card: '#1e1e1e',
            border: '#333333',
            text: '#ffffff',
            textSecondary: '#b3b3b3',
            textMuted: '#808080',
            success: '#4caf50',
            warning: '#ff9800',
            error: '#f44336'
        },
        effects: {
            glassmorphism: false,
            blur: 0,
            cardOpacity: 1
        }
    },
    {
        id: 'ocean',
        name: 'Ocean Deep',
        version: '1.0.0',
        author: 'LOUST',
        type: 'dark',
        background: {
            type: 'gradient',
            value: 'linear-gradient(180deg, #0a1628 0%, #0d2137 50%, #061018 100%)'
        },
        colors: {
            primary: '#00b4d8',
            background: '#0a1628',
            card: '#0d2137',
            border: '#1a3a5c',
            text: '#ffffff',
            textSecondary: '#90caf9',
            textMuted: '#5c8ab8',
            success: '#00e676',
            warning: '#ffc107',
            error: '#ef5350'
        },
        effects: {
            glassmorphism: true,
            blur: 14,
            cardOpacity: 0.6
        }
    }
];

// Estado inicial
const initialState: ThemeState = {
    currentThemeId: 'default-dark',
    customWallpaper: null,
    themes: DEFAULT_THEMES
};

// Cargar estado desde localStorage
function loadState(): ThemeState {
    if (!browser) return initialState;
    
    try {
        const saved = localStorage.getItem('netboozt_theme_state');
        if (saved) {
            const parsed = JSON.parse(saved);
            // Merge con temas por defecto (por si hay actualizaciones)
            return {
                ...parsed,
                themes: [...DEFAULT_THEMES, ...(parsed.customThemes || [])]
            };
        }
    } catch (e) {
        console.error('Error cargando estado de temas:', e);
    }
    return initialState;
}

// Store principal
function createThemeStore() {
    const { subscribe, set, update } = writable<ThemeState>(loadState());
    
    // Guardar cambios automáticamente
    if (browser) {
        subscribe(state => {
            try {
                localStorage.setItem('netboozt_theme_state', JSON.stringify({
                    currentThemeId: state.currentThemeId,
                    customWallpaper: state.customWallpaper,
                    customThemes: state.themes.filter(t => !DEFAULT_THEMES.find(d => d.id === t.id))
                }));
            } catch (e) {
                console.error('Error guardando estado de temas:', e);
            }
        });
    }
    
    return {
        subscribe,
        
        // Cambiar tema
        setTheme: (themeId: string) => {
            update(state => {
                if (state.themes.find(t => t.id === themeId)) {
                    return { ...state, currentThemeId: themeId };
                }
                return state;
            });
        },
        
        // Establecer wallpaper personalizado
        setWallpaper: (url: string | null) => {
            update(state => ({
                ...state,
                customWallpaper: url
            }));
        },
        
        // Agregar tema personalizado
        addCustomTheme: (theme: Theme) => {
            update(state => ({
                ...state,
                themes: [...state.themes, theme]
            }));
        },
        
        // Eliminar tema personalizado
        removeCustomTheme: (themeId: string) => {
            update(state => ({
                ...state,
                themes: state.themes.filter(t => t.id !== themeId || DEFAULT_THEMES.find(d => d.id === themeId)),
                currentThemeId: state.currentThemeId === themeId ? 'default-dark' : state.currentThemeId
            }));
        },
        
        // Reset a default
        reset: () => {
            set(initialState);
        }
    };
}

// Exportar stores
export const themeState = createThemeStore();

// Store derivado para tema actual
export const currentTheme = derived(themeState, $state => {
    return $state.themes.find(t => t.id === $state.currentThemeId) || DEFAULT_THEMES[0];
});

// Store derivado para CSS variables
export const themeCSS = derived([currentTheme, themeState], ([$theme, $state]) => {
    const colors = $theme.colors;
    const effects = $theme.effects;
    
    let backgroundCSS = '';
    if ($state.customWallpaper) {
        backgroundCSS = `url('${$state.customWallpaper}')`;
    } else if ($theme.background.type === 'image') {
        backgroundCSS = `url('${$theme.background.value}')`;
    } else if ($theme.background.type === 'gradient') {
        backgroundCSS = $theme.background.value;
    } else {
        backgroundCSS = $theme.background.value;
    }
    
    return `
        --primary: ${colors.primary};
        --bg: ${colors.background};
        --bg-card: ${colors.card};
        --border: ${colors.border};
        --text-primary: ${colors.text};
        --text-secondary: ${colors.textSecondary};
        --text-muted: ${colors.textMuted};
        --success: ${colors.success};
        --warning: ${colors.warning};
        --error: ${colors.error};
        --glassmorphism-enabled: ${effects.glassmorphism ? 1 : 0};
        --blur-amount: ${effects.blur}px;
        --card-opacity: ${effects.cardOpacity};
        --app-background: ${$theme.background.type === 'solid' ? $theme.background.value : 'transparent'};
        --app-background-image: ${$state.customWallpaper || ($theme.background.type !== 'solid' ? $theme.background.value : 'none')};
    `;
});

// Helpers
export function setTheme(themeId: string) {
    themeState.setTheme(themeId);
}

export function setWallpaper(url: string | null) {
    themeState.setWallpaper(url);
}

export function getAvailableThemes(): Theme[] {
    return get(themeState).themes;
}
