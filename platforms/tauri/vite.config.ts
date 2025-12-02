import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
	
	// Tauri expects a fixed port
	server: {
		port: 1420,
		strictPort: true,
		watch: {
			// Tell vite to ignore watching `src-tauri`
			ignored: ['**/src-tauri/**'],
		},
	},
	
	// Prevent vite from obscuring rust errors
	clearScreen: false,
	
	// Env prefix for Tauri
	envPrefix: ['VITE_', 'TAURI_'],
	
	build: {
		// Tauri uses Chromium on Windows and WebKit on macOS/Linux
		target: process.env.TAURI_PLATFORM == 'windows' ? 'chrome105' : 'safari13',
		// Don't minify for debug builds
		minify: !process.env.TAURI_DEBUG ? 'esbuild' : false,
		// Produce sourcemaps for debug builds
		sourcemap: !!process.env.TAURI_DEBUG,
	},
});
