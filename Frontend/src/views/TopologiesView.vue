<template>
    <div class="content-LM">
        <LearningMaterial />
    </div>
</template>
<script>
import LearningMaterial from "@/components/LearningMaterial.vue";
export default {
    name: "TopologiesView",
    components: {
        LearningMaterial,
    },
};
</script>
<style scoped>
.content-LM {
    background: var(--nlb-gradient-secondary);
}
</style>
