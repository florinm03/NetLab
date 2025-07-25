<template>
    <div class="saved-pcaps-view">
        <SavedPcaps />
    </div>
</template>

<script>
import SavedPcaps from "@/components/SavedPcaps.vue";

export default {
    name: "SavedPcapsView",
    components: {
        SavedPcaps,
    },
};
</script>

<style scoped>
.saved-pcaps-view {
    background: var(--nlb-gradient-secondary);
    min-height: 100vh;
}
</style> 