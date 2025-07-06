<template>
    <div class="network-analyzer">
        <!-- Header Section -->
        <div class="header-section">
            <div class="header-content">
                <div class="header-text">
                    <h1 class="main-title">Netzwerk-Topologie Analyse</h1>
                    <p class="subtitle">
                        Visualisierung des Netzwerkverkehrs und der
                        Kommunikationsmuster
                    </p>
                </div>
                <div class="header-stats">
                    <div class="stat-card">
                        <div class="stat-number">{{ totalNodes }}</div>
                        <div class="stat-label">Knoten</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{{ totalConnections }}</div>
                        <div class="stat-label">Verbindungen</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{{ totalPackets }}</div>
                        <div class="stat-label">Pakete</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Visualization Section -->
        <div class="visualization-section">
            <div class="graph-container">
                <div class="table-header">
                    <h2>Netzwerk-Topologie</h2>

                    <div class="filter-chips">
                        <button @click="resetLayout" class="filter-chip">
                            Layout zurücksetzen
                        </button>
                        <button @click="centerGraph" class="filter-chip">
                            Zentrieren
                        </button>
                        <button
                            @click="
                                showLabels = !showLabels;
                                updateLabels();
                            "
                            :class="['filter-chip', { active: showLabels }]"
                        >
                            Labels anzeigen
                        </button>
                        <button
                            @click="
                                showHighTraffic = !showHighTraffic;
                                updateVisualization();
                            "
                            :class="[
                                'filter-chip',
                                { active: showHighTraffic },
                            ]"
                        >
                            Nur hoher Traffic
                        </button>
                        <span v-if="selectedNode" class="results-count">
                            Ausgewählt: {{ selectedNode.id }} ({{
                                selectedNode.total
                            }}
                            Pakete)
                        </span>
                    </div>
                </div>

                <div class="graph-wrapper">
                    <svg ref="svgRef" class="network-svg"></svg>

                    <!-- Modern Legend -->
                    <div class="legend-panel">
                        <h3>Legende</h3>
                        <div class="legend-items">
                            <div class="legend-item">
                                <div class="legend-circle regular"></div>
                                <span>Standard IP-Adressen</span>
                            </div>
                            <div class="legend-item">
                                <div class="legend-circle multicast"></div>
                                <span>Multicast IP-Adressen</span>
                            </div>
                            <div class="legend-item">
                                <div class="legend-line thin"></div>
                                <span>Geringer Traffic (&lt; 20 Pakete)</span>
                            </div>
                            <div class="legend-item">
                                <div class="legend-line thick"></div>
                                <span>Hoher Traffic (&gt; 50 Pakete)</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Network Statistics -->
        <div class="stats-section">
            <div class="stats-grid">
                <div class="stats-card">
                    <h3>Top Kommunikation</h3>
                    <div class="stats-list">
                        <div
                            v-for="conn in topConnections"
                            :key="`${conn.source}-${conn.destination}`"
                            class="stats-item"
                        >
                            <div class="connection-info">
                                <span class="source">{{ conn.source }}</span>
                                <span class="arrow">→</span>
                                <span class="target">{{
                                    conn.destination
                                }}</span>
                            </div>
                            <span class="packet-count"
                                >{{ conn.value }} Pakete</span
                            >
                        </div>
                    </div>
                </div>

                <div class="stats-card">
                    <h3>Aktivste Knoten</h3>
                    <div class="stats-list">
                        <div
                            v-for="node in topNodes"
                            :key="node.id"
                            class="stats-item"
                        >
                            <div class="node-info">
                                <div
                                    :class="[
                                        'node-indicator',
                                        {
                                            multicast:
                                                node.id.startsWith('224.'),
                                        },
                                    ]"
                                ></div>
                                <span class="node-ip">{{ node.id }}</span>
                            </div>
                            <span class="packet-count"
                                >{{ node.total }} Pakete</span
                            >
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Instructions -->
        <div class="instructions">
            <p>
                <i class="pi pi-lightbulb" />
                <strong> Interaktion:</strong> Bewegen Sie die Maus über Knoten
                und Verbindungen für Details • Ziehen Sie Knoten zum Neuanordnen
            </p>
        </div>
    </div>
</template>

<script>
import * as d3 from "d3";

export default {
    name: "EnhancedNetworkGraph",
    data() {
        return {
            isAnimating: true,
            showLabels: true,
            showHighTraffic: false,
            selectedNode: null,
            simulation: null,
            nodes: [],
            links: [],
            rawData: [
                {
                    source: "172.104.0.102",
                    destination: "224.0.0.22",
                    packets: 12,
                },
                {
                    source: "172.104.0.102",
                    destination: "224.0.0.5",
                    packets: 78,
                },
                {
                    source: "172.103.0.102",
                    destination: "224.0.0.5",
                    packets: 84,
                },
                {
                    source: "172.102.0.102",
                    destination: "224.0.0.5",
                    packets: 89,
                },
                {
                    source: "172.101.0.102",
                    destination: "224.0.0.5",
                    packets: 89,
                },
                {
                    source: "172.103.0.102",
                    destination: "224.0.0.22",
                    packets: 12,
                },
                {
                    source: "172.101.0.102",
                    destination: "224.0.0.22",
                    packets: 12,
                },
                {
                    source: "172.102.0.102",
                    destination: "224.0.0.22",
                    packets: 12,
                },
                {
                    source: "172.104.0.106",
                    destination: "224.0.0.22",
                    packets: 12,
                },
                {
                    source: "172.104.0.106",
                    destination: "224.0.0.5",
                    packets: 71,
                },
                {
                    source: "172.101.0.103",
                    destination: "224.0.0.5",
                    packets: 77,
                },
                {
                    source: "172.102.0.104",
                    destination: "224.0.0.5",
                    packets: 77,
                },
                {
                    source: "172.103.0.105",
                    destination: "224.0.0.5",
                    packets: 81,
                },
                {
                    source: "172.101.0.103",
                    destination: "172.101.0.102",
                    packets: 12,
                },
                {
                    source: "172.102.0.104",
                    destination: "172.102.0.102",
                    packets: 12,
                },
                {
                    source: "172.103.0.105",
                    destination: "172.103.0.102",
                    packets: 10,
                },
                {
                    source: "172.104.0.102",
                    destination: "172.104.0.106",
                    packets: 10,
                },
                {
                    source: "172.103.0.102",
                    destination: "172.103.0.105",
                    packets: 10,
                },
                {
                    source: "172.102.0.102",
                    destination: "172.102.0.104",
                    packets: 10,
                },
                {
                    source: "172.101.0.102",
                    destination: "172.101.0.103",
                    packets: 10,
                },
                {
                    source: "172.101.0.103",
                    destination: "224.0.0.22",
                    packets: 6,
                },
                {
                    source: "172.102.0.104",
                    destination: "224.0.0.22",
                    packets: 6,
                },
                {
                    source: "172.103.0.105",
                    destination: "224.0.0.22",
                    packets: 6,
                },
                {
                    source: "172.104.0.106",
                    destination: "172.104.0.102",
                    packets: 8,
                },
                {
                    source: "172.104.0.102",
                    destination: "224.0.0.6",
                    packets: 3,
                },
            ],
        };
    },
    computed: {
        totalNodes() {
            return this.nodes.length;
        },
        totalConnections() {
            return this.links.length;
        },
        totalPackets() {
            return this.rawData.reduce((sum, d) => sum + d.packets, 0);
        },
        topConnections() {
            return this.rawData
                .sort((a, b) => b.packets - a.packets)
                .slice(0, 5);
        },
        topNodes() {
            return this.nodes.sort((a, b) => b.total - a.total).slice(0, 5);
        },
    },
    mounted() {
        this.initGraph();
        window.addEventListener("resize", this.handleResize);
    },
    beforeUnmount() {
        d3.select("body").selectAll(".tooltip").remove();
        window.removeEventListener("resize", this.handleResize);
        if (this.simulation) {
            this.simulation.stop();
        }
    },
    methods: {
        initGraph() {
            // Process data
            this.processData();

            // Clear previous visualization
            const svg = d3.select(this.$refs.svgRef);
            svg.selectAll("*").remove();

            // Setup dimensions
            const containerWidth = this.$refs.svgRef.parentElement.clientWidth;
            const width = Math.min(containerWidth - 40, 900);
            const height = 600;

            svg.attr("width", width)
                .attr("height", height)
                .attr("viewBox", [0, 0, width, height]);

            // Create container group
            const g = svg.append("g");

            // Add zoom behavior
            const zoom = d3
                .zoom()
                .scaleExtent([0.5, 3])
                .on("zoom", (event) => {
                    g.attr("transform", event.transform);
                });

            svg.call(zoom);

            // Create tooltip
            this.createTooltip();

            // Create force simulation
            this.simulation = d3
                .forceSimulation(this.nodes)
                .force(
                    "link",
                    d3
                        .forceLink(this.links)
                        .id((d) => d.id)
                        .distance((d) => this.getLinkDistance(d)),
                )
                .force(
                    "charge",
                    d3.forceManyBody().strength((d) => this.getNodeCharge(d)),
                )
                .force("center", d3.forceCenter(width / 2, height / 2))
                .force(
                    "collision",
                    d3.forceCollide().radius((d) => this.getNodeRadius(d) + 10),
                );

            // Create arrow markers
            this.createArrowMarkers(svg);

            // Draw links
            this.linkElements = g
                .append("g")
                .attr("class", "links")
                .selectAll("line")
                .data(this.links)
                .join("line")
                .attr("class", "link")
                .attr("stroke", (d) => this.getLinkColor(d))
                .attr("stroke-width", (d) => this.getLinkWidth(d))
                .attr("stroke-opacity", 0.8)
                .attr("marker-end", "url(#arrowhead)")
                .on("mouseover", (event, d) => this.showLinkTooltip(event, d))
                .on("mouseout", () => this.hideTooltip());

            // Draw nodes
            this.nodeElements = g
                .append("g")
                .attr("class", "nodes")
                .selectAll("circle")
                .data(this.nodes)
                .join("circle")
                .attr("class", "node")
                .attr("r", (d) => this.getNodeRadius(d))
                .attr("fill", (d) => this.getNodeColor(d))
                .attr("stroke", "#fff")
                .attr("stroke-width", 2)
                .style("filter", "drop-shadow(0 2px 4px rgba(0,0,0,0.1))")
                .on("mouseover", (event, d) => this.showNodeTooltip(event, d))
                .on("mouseout", () => this.hideTooltip())
                .on("click", (event, d) => this.selectNode(d))
                .call(
                    d3
                        .drag()
                        .on("start", (event, d) => this.dragStarted(event, d))
                        .on("drag", (event, d) => this.dragged(event, d))
                        .on("end", (event, d) => this.dragEnded(event, d)),
                );

            // Add labels
            this.labelElements = g
                .append("g")
                .attr("class", "labels")
                .selectAll("text")
                .data(this.nodes)
                .join("text")
                .attr("class", "label")
                .attr("text-anchor", "middle")
                .attr("dy", (d) => this.getNodeRadius(d) + 16)
                .attr("font-size", "11px")
                .attr("font-weight", "500")
                .attr("fill", "#374151")
                .text((d) => d.id)
                .style("pointer-events", "none")
                .style("display", this.showLabels ? "block" : "none");

            // Update positions on simulation tick
            this.simulation.on("tick", () => {
                this.linkElements
                    .attr("x1", (d) => d.source.x)
                    .attr("y1", (d) => d.source.y)
                    .attr("x2", (d) => d.target.x)
                    .attr("y2", (d) => d.target.y);

                this.nodeElements.attr("cx", (d) => d.x).attr("cy", (d) => d.y);

                this.labelElements.attr("x", (d) => d.x).attr("y", (d) => d.y);
            });
        },

        processData() {
            // Filter data
            let filteredData = this.rawData;

            if (this.showHighTraffic) {
                filteredData = filteredData.filter((d) => d.packets > 20);
            }

            // Extract unique nodes
            const nodeIds = new Set([
                ...filteredData.map((d) => d.source),
                ...filteredData.map((d) => d.destination),
            ]);

            this.nodes = Array.from(nodeIds).map((id) => ({ id }));

            // Calculate totals for each node
            const nodeTotals = {};
            filteredData.forEach((d) => {
                nodeTotals[d.source] = (nodeTotals[d.source] || 0) + d.packets;
                nodeTotals[d.destination] =
                    (nodeTotals[d.destination] || 0) + d.packets;
            });

            this.nodes.forEach((node) => {
                node.total = nodeTotals[node.id] || 0;
            });

            // Create links
            this.links = filteredData.map((d) => ({
                source: d.source,
                target: d.destination,
                value: d.packets,
            }));
        },

        createTooltip() {
            this.tooltip = d3
                .select("body")
                .append("div")
                .attr("class", "modern-tooltip")
                .style("position", "absolute")
                .style("visibility", "hidden")
                .style("background", "rgba(0, 0, 0, 0.9)")
                .style("color", "white")
                .style("padding", "12px 16px")
                .style("border-radius", "8px")
                .style("font-size", "13px")
                .style("font-weight", "500")
                .style("pointer-events", "none")
                .style("box-shadow", "0 4px 6px -1px rgba(0, 0, 0, 0.1)")
                .style("z-index", "1000");
        },

        createArrowMarkers(svg) {
            const defs = svg.append("defs");

            defs.append("marker")
                .attr("id", "arrowhead")
                .attr("viewBox", "0 -5 10 10")
                .attr("refX", 8)
                .attr("refY", 0)
                .attr("markerWidth", 6)
                .attr("markerHeight", 6)
                .attr("orient", "auto")
                .append("path")
                .attr("d", "M0,-5L10,0L0,5")
                .attr("fill", "#6b7280");
        },

        getNodeRadius(d) {
            return Math.max(8, Math.sqrt(d.total) * 0.8 + 4);
        },

        getNodeColor(d) {
            if (d.id.startsWith("224.")) {
                return "#f59e0b"; // Multicast - amber
            }
            return "#6366f1"; // Regular - indigo
        },

        getNodeCharge(d) {
            return d.id.startsWith("224.") ? -800 : -400;
        },

        getLinkDistance(d) {
            return d.value > 50 ? 80 : 120;
        },

        getLinkWidth(d) {
            return Math.max(1, Math.sqrt(d.value) * 0.3);
        },

        getLinkColor(d) {
            if (d.value > 50) return "#dc2626"; // High traffic - red
            if (d.value > 20) return "#f59e0b"; // Medium traffic - amber
            return "#6b7280"; // Low traffic - gray
        },

        showNodeTooltip(event, d) {
            this.tooltip.style("visibility", "visible").html(`
                    <div><strong>${d.id}</strong></div>
                    <div>Gesamte Pakete: ${d.total}</div>
                    <div>Typ: ${d.id.startsWith("224.") ? "Multicast" : "Standard"}</div>
                `);
            this.moveTooltip(event);
        },

        showLinkTooltip(event, d) {
            this.tooltip.style("visibility", "visible").html(`
                    <div><strong>Verbindung</strong></div>
                    <div>Von: ${d.source.id}</div>
                    <div>Zu: ${d.target.id}</div>
                    <div>Pakete: ${d.value}</div>
                `);
            this.moveTooltip(event);
        },

        hideTooltip() {
            this.tooltip.style("visibility", "hidden");
        },

        moveTooltip(event) {
            this.tooltip
                .style("top", event.pageY - 10 + "px")
                .style("left", event.pageX + 10 + "px");
        },

        selectNode(d) {
            this.selectedNode = d;

            // Highlight connected links
            this.linkElements
                .attr("stroke-opacity", (link) =>
                    link.source.id === d.id || link.target.id === d.id
                        ? 1
                        : 0.3,
                )
                .attr("stroke-width", (link) =>
                    link.source.id === d.id || link.target.id === d.id
                        ? this.getLinkWidth(link) + 1
                        : this.getLinkWidth(link),
                );

            // Highlight connected nodes
            this.nodeElements
                .attr("stroke", (node) => (node.id === d.id ? "#000" : "#fff"))
                .attr("stroke-width", (node) => (node.id === d.id ? 3 : 2));
        },

        resetLayout() {
            if (this.simulation) {
                this.simulation.alpha(1).restart();
            }
        },

        centerGraph() {
            const svg = d3.select(this.$refs.svgRef);

            svg.transition()
                .duration(750)
                .call(
                    d3.zoom().transform,
                    d3.zoomIdentity.translate(0, 0).scale(1),
                );
        },

        updateVisualization() {
            this.initGraph();
        },

        updateLabels() {
            if (this.labelElements) {
                this.labelElements.style(
                    "display",
                    this.showLabels ? "block" : "none",
                );
            }
        },

        handleResize() {
            clearTimeout(this.resizeTimeout);
            this.resizeTimeout = setTimeout(() => {
                this.initGraph();
            }, 300);
        },

        dragStarted(event, d) {
            if (!event.active) this.simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        },

        dragged(event, d) {
            d.fx = event.x;
            d.fy = event.y;
        },

        dragEnded(event, d) {
            if (!event.active) this.simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        },
    },
};
</script>

<style scoped>
.network-analyzer {
    font-family:
        -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

/* Header Section */
.header-section {
    background: var(--nlb-gradient-primary);
    color: var(--nlb-text-light);
    padding: 4rem 2rem 3rem;
}

.header-content {
    max-width: 1200px;
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 2rem;
}

.main-title {
    font-size: 3rem;
    font-weight: 700;
    margin: 0 0 1rem 0;
    background: linear-gradient(45deg, var(--nlb-text-light), #e3f2fd);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.subtitle {
    font-size: 1.1rem;
    opacity: 0.9;
    line-height: 1.6;
    margin: 0;
    max-width: 600px;
}

.header-stats {
    display: flex;
    gap: 1rem;
}

.stat-card {
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
    min-width: 120px;
}

.stat-number {
    font-size: 1.75rem;
    font-weight: 700;
    margin-bottom: 0.25rem;
}

.stat-label {
    font-size: 0.9rem;
    opacity: 0.8;
}

/* Visualization Section */
.visualization-section {
    overflow: hidden;
}

.graph-container {
    max-width: 1200px;
    margin: 0 auto;
    background: var(--nlb-bg-primary);
    overflow: hidden;
}

.table-header {
    padding: 1.5rem 2rem;
    border-bottom: 1px solid var(--nlb-border-light);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    align-items: flex-start;
    gap: 1.5rem;
    flex-wrap: wrap;
}

.table-header h2 {
    margin: 0;
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--nlb-text-primary);
}

.filter-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
    align-items: center;
}

.filter-chip {
    padding: 0.5rem 1rem;
    border: 2px solid var(--nlb-border-light);
    border-radius: 20px;
    background: var(--nlb-bg-primary);
    color: var(--nlb-text-secondary);
    font-size: 0.875rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
}

.filter-chip:hover {
    border-color: var(--nlb-primary);
    color: var(--nlb-primary);
}

.filter-chip.active {
    background: var(--nlb-primary);
    border-color: var(--nlb-primary);
    color: var(--nlb-text-light);
}

.results-count {
    color: var(--nlb-text-secondary);
    font-size: 0.875rem;
    font-weight: 500;
}

.graph-wrapper {
    position: relative;
    padding: 2rem;
}

.network-svg {
    width: 100%;
    height: 600px;
    border-radius: 8px;
    background:
        linear-gradient(45deg, var(--nlb-bg-secondary) 25%, transparent 25%),
        linear-gradient(-45deg, var(--nlb-bg-secondary) 25%, transparent 25%),
        linear-gradient(45deg, transparent 75%, var(--nlb-bg-secondary) 75%),
        linear-gradient(-45deg, transparent 75%, var(--nlb-bg-secondary) 75%);
    background-size: 20px 20px;
    background-position:
        0 0,
        0 10px,
        10px -10px,
        -10px 0px;
}

/* Legend Panel */
.legend-panel {
    position: absolute;
    top: 2rem;
    right: 2rem;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    border: 1px solid var(--nlb-border-light);
    border-radius: 12px;
    padding: 1rem 1.5rem;
    min-width: 200px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.legend-panel h3 {
    margin: 0 0 1rem 0;
    font-size: 1rem;
    font-weight: 600;
    color: var(--nlb-text-primary);
}

.legend-items {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.legend-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-size: 0.875rem;
    color: var(--nlb-text-primary);
}

.legend-circle {
    width: 12px;
    height: 12px;
    border-radius: 50%;
}

.legend-circle.regular {
    background: var(--nlb-primary);
}

.legend-circle.multicast {
    background: var(--nlb-warning);
}

.legend-line {
    width: 24px;
    height: 2px;
    background: var(--nlb-text-secondary);
}

.legend-line.thin {
    height: 1px;
}

.legend-line.thick {
    height: 4px;
}

/* Statistics Section */
.stats-section {
    padding: 2rem;
}

.stats-grid {
    max-width: 1200px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
}

.stats-card {
    background: var(--nlb-bg-primary);
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 20px 40px rgba(79, 70, 229, 0.15);
}

.stats-card h3 {
    margin: 0 0 1rem 0;
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--nlb-text-primary);
}

.stats-list {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.stats-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem;
    background: var(--nlb-bg-secondary);
    border-radius: 8px;
    border-left: 3px solid var(--nlb-primary);
}

.connection-info {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-family: monospace;
    font-size: 0.875rem;
}

.source,
.target {
    color: var(--nlb-text-primary);
    font-weight: 500;
}

.arrow {
    color: var(--nlb-text-secondary);
    font-weight: bold;
}

.node-info {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.node-indicator {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: var(--nlb-primary);
}

.node-indicator.multicast {
    background: var(--nlb-warning);
}

.node-ip {
    font-family: monospace;
    font-size: 0.875rem;
    color: var(--nlb-text-primary);
    font-weight: 500;
}

.packet-count {
    font-size: 0.875rem;
    color: var(--nlb-text-secondary);
    font-weight: 600;
}

/* Instructions */
.instructions {
    padding: 1rem 2rem 2rem;
    text-align: center;
    color: #6b7280;
    font-size: 0.875rem;
}

/* Global tooltip styles */
:global(.modern-tooltip) {
    font-family:
        -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
}

/* SVG Styles */
:deep(.node) {
    cursor: pointer;
    transition: all 0.2s ease;
}

:deep(.node:hover) {
    stroke: #000 !important;
    stroke-width: 3px !important;
}

:deep(.link) {
    cursor: pointer;
    transition: all 0.2s ease;
}

:deep(.link:hover) {
    stroke-opacity: 1 !important;
}

:deep(.label) {
    font-family:
        -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    user-select: none;
}

/* Responsive Design */
@media (max-width: 1024px) {
    .header-content {
        flex-direction: column;
        text-align: center;
        gap: 1.5rem;
    }

    .header-stats {
        justify-content: center;
    }

    .table-header {
        flex-direction: column;
        gap: 1.5rem;
        align-items: flex-start;
    }

    .filter-chips {
        width: 100%;
        justify-content: center;
    }

    .stats-grid {
        grid-template-columns: 1fr;
        gap: 1.5rem;
    }

    .legend-panel {
        position: static;
        margin-top: 1rem;
        width: 100%;
    }

    .graph-wrapper {
        padding: 1rem;
    }
}

@media (max-width: 768px) {
    .main-title {
        font-size: 2rem;
    }

    .network-analyzer {
        padding: 0;
    }

    .header-section {
        padding: 2rem 1rem 1.5rem;
    }

    .visualization-section {
        padding: 1rem;
        margin: 0;
        border-radius: 0;
    }

    .stats-section {
        padding: 1rem;
    }

    .table-header {
        flex-direction: column;
        gap: 1rem;
        align-items: center;
        text-align: center;
    }

    .filter-chips {
        justify-content: center;
    }

    .connection-info {
        flex-direction: column;
        gap: 0.25rem;
        text-align: center;
    }

    .stats-item {
        flex-direction: column;
        gap: 0.5rem;
        align-items: flex-start;
        text-align: center;
    }
}

/* Animation for initial load */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.graph-container {
    animation: fadeInUp 0.6s ease-out;
}

.stats-card {
    animation: fadeInUp 0.6s ease-out;
}

.stats-card:nth-child(2) {
    animation-delay: 0.1s;
}

/* Focus styles for accessibility */
.filter-chip:focus {
    outline: 2px solid var(--nlb-primary);
    outline-offset: 2px;
}
</style>
