<template>
    <div class="topology-graph-container">
        <!-- Graph Header -->
        <div class="graph-header">
            <h3>Topologie Visualisierung</h3>
        </div>

        <!-- Simple Graph Visualization -->
        <div class="graph-canvas" ref="graphContainer">
            <div class="graph-wrapper">
                <div class="nodes-container">
                    <div 
                        v-for="(node, index) in nodes" 
                        :key="node.id"
                        class="graph-node"
                        :style="getNodePosition(index)"
                    >
                        <div class="node-circle">
                            <span class="node-number">{{ getNodeDisplayName(node.name, index) }}</span>
                        </div>
                    </div>
                </div>
                
                <!-- Connections -->
                <svg class="connections-svg">
                    <line 
                        v-for="connection in connections" 
                        :key="`${connection.source}-${connection.target}`"
                        :x1="getConnectionStart(connection).x"
                        :y1="getConnectionStart(connection).y"
                        :x2="getConnectionEnd(connection).x"
                        :y2="getConnectionEnd(connection).y"
                        class="connection-line"
                    />
                </svg>
            </div>
        </div>
    </div>
</template>

<script>
import Button from 'primevue/button';

export default {
    name: 'TopologyGraph',
    components: {
        Button
    },
    props: {
        nodes: {
            type: Array,
            default: () => []
        },
        connections: {
            type: Array,
            default: () => []
        }
    },
    data() {
        return {
            nodeRadius: 30,
            containerWidth: 600,
            containerHeight: 400,
            visibilityObserver: null
        };
    },
    mounted() {
        this.updateContainerSize();
        window.addEventListener('resize', this.updateContainerSize);
        
        // Listen for visibility change events (tab switching)
        document.addEventListener('visibilitychange', this.handleVisibilityChange);
        
        // Use MutationObserver to detect when the component becomes visible
        this.observeVisibility();
    },
    beforeUnmount() {
        window.removeEventListener('resize', this.updateContainerSize);
        document.removeEventListener('visibilitychange', this.handleVisibilityChange);
        
        if (this.visibilityObserver) {
            this.visibilityObserver.disconnect();
        }
    },
    watch: {
        nodes: {
            handler() {
                this.$nextTick(() => {
                    this.updateContainerSize();
                });
            },
            deep: true
        }
    },
    methods: {
        updateContainerSize() {
            const container = this.$refs.graphContainer;
            if (container) {
                this.$nextTick(() => {
                    const newWidth = container.clientWidth;
                    const newHeight = container.clientHeight;
                    
                    // Only update if dimensions actually changed
                    if (newWidth !== this.containerWidth || newHeight !== this.containerHeight) {
                        this.containerWidth = newWidth;
                        this.containerHeight = newHeight;
                    }
                });
            }
        },
        
        handleVisibilityChange() {
            if (!document.hidden) {
                setTimeout(() => {
                    this.updateContainerSize();
                }, 100);
            }
        },
        
        observeVisibility() {
            // Use Intersection Observer to detect when component becomes visible
            if ('IntersectionObserver' in window) {
                this.visibilityObserver = new IntersectionObserver((entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            setTimeout(() => {
                                this.updateContainerSize();
                            }, 50);
                        }
                    });
                }, {
                    threshold: 0.1
                });
                
                // Use nextTick to ensure DOM is ready
                this.$nextTick(() => {
                    if (this.$refs.graphContainer) {
                        this.visibilityObserver.observe(this.$refs.graphContainer);
                    }
                });
            }
        },
        
        getNodePosition(index) {
            const nodeCount = this.nodes.length;
            if (nodeCount === 0) return {};
            
            const centerX = this.containerWidth / 2;
            const centerY = this.containerHeight / 2;
            const radius = Math.min(this.containerWidth, this.containerHeight) * 0.3;
            
            let x, y;
            
            if (nodeCount === 1) {
                x = centerX;
                y = centerY;
            } else if (nodeCount === 2) {
                x = centerX + (index === 0 ? -radius/2 : radius/2);
                y = centerY;
            } else {
                // Circular arrangement for 3+ nodes
                const angle = (index * 2 * Math.PI) / nodeCount;
                x = centerX + radius * Math.cos(angle);
                y = centerY + radius * Math.sin(angle);
            }
            
            return {
                left: `${x - this.nodeRadius}px`,
                top: `${y - this.nodeRadius}px`
            };
        },
        
        getConnectionStart(connection) {
            const sourceIndex = this.nodes.findIndex(n => n.id === connection.source);
            const targetIndex = this.nodes.findIndex(n => n.id === connection.target);
            
            if (sourceIndex === -1 || targetIndex === -1) return { x: 0, y: 0 };
            
            const sourcePos = this.getNodePosition(sourceIndex);
            const targetPos = this.getNodePosition(targetIndex);
            
            const sourceX = parseFloat(sourcePos.left) + this.nodeRadius;
            const sourceY = parseFloat(sourcePos.top) + this.nodeRadius;
            const targetX = parseFloat(targetPos.left) + this.nodeRadius;
            const targetY = parseFloat(targetPos.top) + this.nodeRadius;
            
            // Calculate connection start point (edge of source node)
            const dx = targetX - sourceX;
            const dy = targetY - sourceY;
            const distance = Math.sqrt(dx * dx + dy * dy);
            
            if (distance === 0) return { x: sourceX, y: sourceY };
            
            const unitX = dx / distance;
            const unitY = dy / distance;
            
            return {
                x: sourceX + unitX * this.nodeRadius,
                y: sourceY + unitY * this.nodeRadius
            };
        },
        
        getConnectionEnd(connection) {
            const sourceIndex = this.nodes.findIndex(n => n.id === connection.source);
            const targetIndex = this.nodes.findIndex(n => n.id === connection.target);
            
            if (sourceIndex === -1 || targetIndex === -1) return { x: 0, y: 0 };
            
            const sourcePos = this.getNodePosition(sourceIndex);
            const targetPos = this.getNodePosition(targetIndex);
            
            const sourceX = parseFloat(sourcePos.left) + this.nodeRadius;
            const sourceY = parseFloat(sourcePos.top) + this.nodeRadius;
            const targetX = parseFloat(targetPos.left) + this.nodeRadius;
            const targetY = parseFloat(targetPos.top) + this.nodeRadius;
            
            // Calculate connection end point (edge of target node)
            const dx = sourceX - targetX;
            const dy = sourceY - targetY;
            const distance = Math.sqrt(dx * dx + dy * dy);
            
            if (distance === 0) return { x: targetX, y: targetY };
            
            const unitX = dx / distance;
            const unitY = dy / distance;
            
            return {
                x: targetX + unitX * this.nodeRadius,
                y: targetY + unitY * this.nodeRadius
            };
        },


        getNodeDisplayName(containerName, index) {
            if (!containerName) {
                return `${index + 1}`;
            }
            
            // Extract the number from container name like:: "prototype-guest_18dbmi_node-guest_18dbmi_101"
            const match = containerName.match(/_(\d+)$/);
            if (match) {
                return match[1];
            }
            
            // Fallback: try to find any number in the name
            const numberMatch = containerName.match(/(\d+)/);
            if (numberMatch) {
                return numberMatch[1];
            }
            
            // Final fallback
            return `${index + 1}`;
        }
    }
};
</script>

<style scoped>
.topology-graph-container {
    background: var(--nlb-bg-primary);
    border: 1px solid var(--nlb-border-light);
    border-radius: 12px;
    box-shadow: 0 4px 20px var(--nlb-border-medium);
    overflow: hidden;
    height: 500px;
    display: flex;
    flex-direction: column;
    margin-bottom: 20px;
}

.graph-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 20px;
    border-bottom: 1px solid var(--nlb-border-light);
    background: var(--nlb-bg-secondary);
}

.graph-header h3 {
    margin: 0;
    color: var(--nlb-text-primary);
    font-size: 18px;
    font-weight: 600;
}

.graph-canvas {
    flex: 1;
    position: relative;
    overflow: hidden;
    background: #fafafa;
}

.graph-wrapper {
    position: relative;
    width: 100%;
    height: 100%;
}

.nodes-container {
    position: relative;
    width: 100%;
    height: 100%;
}

.graph-node {
    position: absolute;
    cursor: pointer;
    transition: all 0.3s ease;
    z-index: 10;
}

.graph-node:hover {
    transform: scale(1.1);
}

.node-circle {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: #4CAF50;
    border: 3px solid #333;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.node-number {
    color: white;
    font-weight: bold;
    font-size: 18px;
}

.node-label {
    text-align: center;
    font-size: 12px;
    font-weight: 600;
    color: var(--nlb-text-primary);
    white-space: nowrap;
}

.connections-svg {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 5;
    pointer-events: none;
}

.connection-line {
    stroke: #666;
    stroke-width: 3;
    fill: none;
    opacity: 0.7;
}
</style> 