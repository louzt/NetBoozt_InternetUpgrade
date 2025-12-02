<!--
    SkeletonCard.svelte - Skeleton para cards de stats y contenido
    
    By LOUST (www.loust.pro)
-->
<script lang="ts">
    import Skeleton from './Skeleton.svelte';
    
    export let variant: 'stat' | 'adapter' | 'dns' | 'profile' | 'alert' | 'setting' = 'stat';
</script>

{#if variant === 'stat'}
    <div class="skeleton-card stat">
        <div class="stat-header">
            <Skeleton variant="circular" width="40px" height="40px" />
            <div class="stat-info">
                <Skeleton width="60px" height="0.75rem" />
                <Skeleton width="80px" height="1.5rem" />
            </div>
        </div>
    </div>

{:else if variant === 'adapter'}
    <div class="skeleton-card adapter">
        <div class="adapter-header">
            <Skeleton width="120px" height="1rem" />
            <Skeleton width="40px" height="1rem" variant="rounded" />
        </div>
        <Skeleton width="200px" height="0.75rem" />
        <div class="adapter-stats">
            <Skeleton width="80px" height="0.75rem" />
            <Skeleton width="120px" height="0.75rem" />
        </div>
    </div>

{:else if variant === 'dns'}
    <div class="skeleton-card dns">
        <div class="dns-header">
            <Skeleton variant="circular" width="48px" height="48px" />
            <Skeleton width="100px" height="1rem" />
        </div>
        <Skeleton width="100%" height="0.75rem" />
        <Skeleton width="80%" height="0.75rem" />
        <div class="dns-features">
            <Skeleton width="60px" height="1.25rem" variant="rounded" />
            <Skeleton width="70px" height="1.25rem" variant="rounded" />
            <Skeleton width="50px" height="1.25rem" variant="rounded" />
        </div>
        <Skeleton width="100%" height="36px" variant="rounded" />
    </div>

{:else if variant === 'profile'}
    <div class="skeleton-card profile">
        <div class="profile-header">
            <Skeleton variant="circular" width="56px" height="56px" />
            <div class="profile-info">
                <Skeleton width="100px" height="1.25rem" />
                <Skeleton width="60px" height="0.75rem" />
            </div>
        </div>
        <Skeleton lines={2} height="0.75rem" />
        <div class="profile-features">
            {#each [1, 2, 3] as _}
                <Skeleton width="100%" height="0.75rem" />
            {/each}
        </div>
        <Skeleton width="100%" height="40px" variant="rounded" />
    </div>

{:else if variant === 'alert'}
    <div class="skeleton-card alert">
        <Skeleton variant="circular" width="32px" height="32px" />
        <div class="alert-content">
            <Skeleton width="200px" height="0.875rem" />
            <Skeleton width="100px" height="0.625rem" />
        </div>
    </div>

{:else if variant === 'setting'}
    <div class="skeleton-card setting">
        <Skeleton width="100px" height="0.875rem" />
        <Skeleton width="60px" height="0.875rem" />
    </div>
{/if}

<style>
    .skeleton-card {
        background: var(--bg-elevated, #2b2b2b);
        border-radius: 12px;
        padding: 1rem;
    }
    
    /* Stat variant */
    .skeleton-card.stat {
        padding: 1.25rem;
    }
    
    .stat-header {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .stat-info {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    
    /* Adapter variant */
    .skeleton-card.adapter {
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
    }
    
    .adapter-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .adapter-stats {
        display: flex;
        gap: 1rem;
        margin-top: 0.5rem;
    }
    
    /* DNS variant */
    .skeleton-card.dns {
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
        padding: 1.25rem;
    }
    
    .dns-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .dns-features {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
    }
    
    /* Profile variant */
    .skeleton-card.profile {
        display: flex;
        flex-direction: column;
        gap: 1rem;
        padding: 1.5rem;
    }
    
    .profile-header {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .profile-info {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .profile-features {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    
    /* Alert variant */
    .skeleton-card.alert {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.75rem;
    }
    
    .alert-content {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 0.375rem;
    }
    
    /* Setting variant */
    .skeleton-card.setting {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.75rem 1rem;
    }
</style>
