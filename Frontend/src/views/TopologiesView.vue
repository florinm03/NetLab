<template>
    <div class="content-LM">
        <LearningMaterial />
    </div>
</template>
<script>
import CarouselGraphs from "@/components/CarouselGraphs.vue";
import LearningMaterial from "@/components/LearningMaterial.vue";
export default {
    name: "TopologiesView",
    components: {
        CarouselGraphs,
        LearningMaterial,
    },
};
</script>
<style scoped>
.content-LM {
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}
</style>
