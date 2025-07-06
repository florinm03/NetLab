<script setup>
import { computed } from "vue";
import { BaseEdge, getBezierPath } from "@vue-flow/core";

const props = defineProps({
    id: {
        type: String,
        required: true,
    },
    source: {
        type: String,
        required: true,
    },
    target: {
        type: String,
        required: true,
    },
    sourceX: {
        type: Number,
        required: true,
    },
    sourceY: {
        type: Number,
        required: true,
    },
    targetX: {
        type: Number,
        required: true,
    },
    targetY: {
        type: Number,
        required: true,
    },
    sourcePosition: {
        type: String,
        required: false,
    },
    targetPosition: {
        type: String,
        required: false,
    },
    data: {
        type: Object,
        required: false,
    },
    markerEnd: {
        type: String,
        required: false,
    },
    style: {
        type: Object,
        required: false,
    },
});

const [edgePath, labelX, labelY] = getBezierPath(
    {},
    {
        sourceX: props.sourceX,
        sourceY: props.sourceY,
        sourcePosition: props.sourcePosition,
        targetX: props.targetX,
        targetY: props.targetY,
        targetPosition: props.targetPosition,
    },
);

const dataText = computed(() => {
    return props.data && props.data.hello ? props.data.hello : "";
});
</script>

<template>
    <BaseEdge
        :id="id"
        :path="edgePath"
        :markerEnd="markerEnd"
        class="special-edge"
    />
    <text
        v-if="dataText"
        :x="labelX"
        :y="labelY"
        text-anchor="middle"
        alignment-baseline="middle"
        class="special-edge-text"
        fill="#ff8c00"
    >
        {{ dataText }}
    </text>
</template>

<style>
.special-edge {
    stroke: #ff8c00;
    stroke-width: 3px;
}

.special-edge-text {
    font-size: 12px;
    pointer-events: none;
    font-weight: bold;
}
</style>
