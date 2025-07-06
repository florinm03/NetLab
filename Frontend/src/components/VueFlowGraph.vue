<script setup>
import "@vue-flow/core/dist/style.css";

import { ref, onMounted } from "vue";

import { VueFlow, useVueFlow } from "@vue-flow/core";

import { MiniMap } from "@vue-flow/minimap";
import { ControlButton, Controls } from "@vue-flow/controls";
import { Background } from "@vue-flow/background";

import Icon from "./Icon.vue";

import SpecialNode from "./SpecialNode.vue";
import SpecialEdge from "./SpecialEdge.vue";

const { onInit, onNodeDragStop, onConnect, addEdges, setViewport, toObject } =
    useVueFlow();
onInit((vueFlowInstance) => {
    vueFlowInstance.fitView();
});

// these are our nodes
const nodes = ref([
    {
        id: "1",
        type: "input",
        position: { x: 250, y: 5 },
        data: { label: "Node 1" },
    },
    {
        id: "2",
        position: { x: 100, y: 100 },
        data: { label: "Node 2" },
    },
    {
        id: "3",
        type: "output",
        position: { x: 400, y: 200 },
        data: { label: "Node 3" },
    },
    {
        id: "4",
        type: "special",
        position: { x: 400, y: 300 },
        data: {
            label: "Node 4",
            hello: "world",
        },
    },
]);

// these are our edges
const edges = ref([
    {
        id: "e1->2",
        source: "1",
        target: "2",
    },
    {
        id: "e2->3",
        source: "2",
        target: "3",
        animated: true,
    },
    {
        id: "e3->4",
        type: "special",
        source: "3",
        target: "4",
        data: {
            hello: "world",
        },
    },
]);
</script>

<template>
    <div class="flow">
        <VueFlow :nodes="nodes" :edges="edges">
            <Background pattern-color="#aaa" :gap="16" />
            <MiniMap
                position="bottom-left"
                :style="{ backgroundColor: '#aaa' }"
                :pannable="true"
                :zoomable="true"
            />
            <Controls position="top-left"> </Controls>
            <!-- Custom node template -->
            <template #node-special="specialNodeProps">
                <SpecialNode v-bind="specialNodeProps" />
            </template>

            <!-- Custom edge template -->
            <template #edge-special="specialEdgeProps">
                <SpecialEdge v-bind="specialEdgeProps" />
            </template>
        </VueFlow>
    </div>
</template>

<style>
.flow {
    width: 100%;
    height: auto;
    aspect-ratio: 16 / 9;
    position: relative;
    background-color: #f9f9f9;
    border: 1px solid #ddd;
    border-radius: 8px;
    overflow: hidden;
    box-shadow:
        0 4px 6px rgba(0, 0, 0, 0.1),
        0 1px 3px rgba(0, 0, 0, 0.06);
}

.vue-flow__node {
    font-family: Arial, sans-serif;
    font-size: 14px;
    color: #333;
    background-color: #fff;
    border: 1px solid #ccc;
    border-radius: 4px;
    padding: 8px;
    text-align: center;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    cursor: pointer;
    transition:
        transform 0.2s ease,
        box-shadow 0.2s ease;
}

.vue-flow__node:hover {
    transform: scale(1.05);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.vue-flow__edge {
    stroke: #999;
    stroke-width: 2px;
    transition: stroke 0.2s ease;
}

.vue-flow__edge.animated {
    stroke-dasharray: 5, 5;
    animation: dash 1s linear infinite;
}

@keyframes dash {
    to {
        stroke-dashoffset: -10;
    }
}

.vue-flow__edge:hover {
    stroke: #007ad9;
    stroke-width: 3px;
}

.vue-flow__node--special {
    background-color: #007ad9;
    color: #fff;
    border: none;
    font-weight: bold;
}

.vue-flow__edge--special {
    stroke: #ff8c00;
    stroke-width: 3px;
}
</style>
