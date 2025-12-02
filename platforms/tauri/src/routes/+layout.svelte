<script lang="ts">
	import '../app.css';
	import { onMount } from 'svelte';
	
	// Prevent right-click context menu in production
	onMount(() => {
		if (import.meta.env.PROD) {
			document.addEventListener('contextmenu', (e) => e.preventDefault());
		}
	});
</script>

<slot />
