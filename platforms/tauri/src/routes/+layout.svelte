<script lang="ts">
	import '../app.css';
	import { onMount } from 'svelte';
	
	// SvelteKit page data - ignorar para evitar warnings
	export let data: Record<string, unknown> = {};
	// @ts-ignore - SvelteKit pasa params automáticamente
	let { params } = $$restProps || {};
	$: params; // evitar unused warning
	$: data; // evitar unused warning
	
	// Prevent right-click context menu in production
	onMount(() => {
		if (import.meta.env.PROD) {
			document.addEventListener('contextmenu', (e) => e.preventDefault());
		}
	});
</script>

<slot />
