<script setup>
import LabController from "@/components/LabController.vue";
</script>

<template>
    <main>
        <LabController />
    </main>
</template>

<style scoped>
main {
    display: flex;
    flex-direction: column;

    width: 100%;
    flex: 1;
    overflow: auto;
}
</style>
