<script setup>
// Accept props from the parent component
const props = defineProps({
    id: {
        type: String,
        required: true,
    },
    data: {
        type: Object,
        required: true,
    },
    selected: {
        type: Boolean,
        default: false,
    },
});
</script>

<template>
    <div class="special-node" :class="{ selected: selected }">
        <div class="special-node-header">{{ data.label }}</div>
        <div class="special-node-content" v-if="data.hello">
            Hello: {{ data.hello }}
        </div>
    </div>
</template>

<style scoped>
.special-node {
    padding: 10px;
    background-color: #007ad9;
    color: white;
    border-radius: 5px;
    min-width: 150px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    transition:
        transform 0.3s,
        box-shadow 0.3s;
}

.special-node:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 10px rgba(0, 0, 0, 0.15);
}

.special-node.selected {
    box-shadow: 0 0 0 2px #ff6b6b;
}

.special-node-header {
    font-weight: bold;
    margin-bottom: 5px;
    font-size: 14px;
}

.special-node-content {
    font-size: 12px;
    opacity: 0.9;
}
</style>
