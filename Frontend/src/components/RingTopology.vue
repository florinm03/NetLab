<template>
    <div class="ring-topology-container">
        <VueFlow
            v-model="elements"
            :default-viewport="{ x: 0, y: 0, zoom: 1 }"
            :fit-view-on-init="true"
            class="vue-flow-wrapper"
        >
            <template #node-custom="nodeProps">
                <div class="custom-node">
                    <div class="node-header">{{ nodeProps.label }}</div>
                    <div class="node-id">ID: {{ nodeProps.id }}</div>
                </div>
            </template>

            <template #edge-default="edgeProps">
                <BaseEdge
                    :id="edgeProps.id"
                    :source-node="edgeProps.sourceNode"
                    :target-node="edgeProps.targetNode"
                    :source-handle="edgeProps.sourceHandle"
                    :target-handle="edgeProps.targetHandle"
                    :style="{ stroke: '#ff6b6b', strokeWidth: 2 }"
                />
            </template>

            <Panel position="top-right" class="controls">
                <button @click="addNode">Add Node</button>
                <button @click="removeNode">Remove Node</button>
                <button @click="rearrangeRing">Re-arrange Ring</button>
            </Panel>
        </VueFlow>
    </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { VueFlow, Panel, BaseEdge, useVueFlow } from "@vue-flow/core";
import "@vue-flow/core/dist/style.css";

const { findNode, getNodes, getEdges, addEdges, removeEdges } = useVueFlow();

const elements = ref({
    nodes: [],
    edges: [],
});

// Initial number of nodes in the ring
const initialNodeCount = 6;

// Function to calculate position in a circle
const calculateRingPosition = (index, total, radius = 200) => {
    const angle = (index / total) * 2 * Math.PI;
    const x = radius * Math.cos(angle);
    const y = radius * Math.sin(angle);
    return { x, y };
};

// Create nodes in a ring formation
const createRingNodes = (count) => {
    const nodes = [];

    for (let i = 0; i < count; i++) {
        const position = calculateRingPosition(i, count);
        nodes.push({
            id: `node-${i + 1}`,
            type: "custom",
            label: `Node ${i + 1}`,
            position,
            draggable: true,
        });
    }

    return nodes;
};

// Create edges to connect the ring
const createRingEdges = (nodes) => {
    const edges = [];

    nodes.forEach((node, index) => {
        // Connect to the next node in the ring
        const nextIndex = (index + 1) % nodes.length;
        edges.push({
            id: `edge-${node.id}-${nodes[nextIndex].id}`,
            source: node.id,
            target: nodes[nextIndex].id,
            animated: true,
        });
    });

    return edges;
};

// Function to rearrange nodes in a ring pattern
const rearrangeRing = () => {
    const currentNodes = getNodes();
    const updatedNodes = [...currentNodes];

    updatedNodes.forEach((node, index) => {
        const position = calculateRingPosition(index, updatedNodes.length);
        node.position = position;
    });

    // Update edges
    const currentEdges = getEdges();
    removeEdges(currentEdges.map((edge) => edge.id));
    const newEdges = createRingEdges(updatedNodes);
    addEdges(newEdges);

    elements.value = {
        nodes: updatedNodes,
        edges: newEdges,
    };
};

// Function to add a new node to the ring
const addNode = () => {
    const currentNodes = getNodes();
    const newNodeId = `node-${currentNodes.length + 1}`;

    // Add the new node
    const newNodes = [
        ...currentNodes,
        {
            id: newNodeId,
            type: "custom",
            label: `Node ${currentNodes.length + 1}`,
            position: { x: 0, y: 0 }, // Temporary position, will be rearranged
            draggable: true,
        },
    ];

    elements.value.nodes = newNodes;

    // Rearrange to maintain the ring topology
    rearrangeRing();
};

// Function to remove the last node from the ring
const removeNode = () => {
    const currentNodes = getNodes();
    if (currentNodes.length <= 3) {
        alert("Ring must have at least 3 nodes");
        return;
    }

    // Remove the last node
    const newNodes = currentNodes.slice(0, -1);
    elements.value.nodes = newNodes;

    // Rearrange to maintain the ring topology
    rearrangeRing();
};

// Initialize the ring topology
onMounted(() => {
    const initialNodes = createRingNodes(initialNodeCount);
    const initialEdges = createRingEdges(initialNodes);

    elements.value = {
        nodes: initialNodes,
        edges: initialEdges,
    };
});
</script>

<style scoped>
.ring-topology-container {
    width: 100%;
    height: 600px;
    border: 1px solid #ddd;
    border-radius: 8px;
    overflow: hidden;
}

.vue-flow-wrapper {
    width: 100%;
    height: 100%;
}

.custom-node {
    padding: 10px;
    border-radius: 8px;
    width: 120px;
    background-color: #f5f5f5;
    color: #333;
    border: 2px solid #ff6b6b;
    display: flex;
    flex-direction: column;
    align-items: center;
    font-family: sans-serif;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.node-header {
    font-weight: bold;
    margin-bottom: 5px;
    font-size: 14px;
}

.node-id {
    font-size: 12px;
    color: #666;
}

.controls {
    display: flex;
    gap: 8px;
}

.controls button {
    background-color: #4c4cff;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 12px;
    cursor: pointer;
    font-size: 14px;
    transition: background-color 0.2s;
}

.controls button:hover {
    background-color: #3a3acc;
}
</style>
