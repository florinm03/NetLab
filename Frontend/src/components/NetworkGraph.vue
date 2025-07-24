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
                    <div class="pcap-selection">
                        <Dropdown
                            id="connection-demo-select"
                            v-model="selectedDemo"
                            :options="availableDemos"
                            optionLabel="name"
                            optionValue="path"
                            placeholder="Verbindungs-Demo auswählen"
                            class="pcap-dropdown"
                            @change="loadSelectedDemo"
                            :loading="loading"
                        >
                            <template #option="slotProps">
                                <div class="pcap-option">
                                    <div class="pcap-header">
                                        <span class="pcap-name">{{ slotProps.option.name }}</span>
                                        <span v-if="slotProps.option.type === 'saved'" class="pcap-badge">Gespeichert</span>
                                        <span v-else class="pcap-badge demo">Demo</span>
                                    </div>
                                    <span class="pcap-description">{{ slotProps.option.description }}</span>
                                </div>
                            </template>
                        </Dropdown>
                    </div>
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
                                processData();
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
                                >{{ conn.packets }} Pakete</span
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

<script setup>
import * as d3 from "d3";
import Dropdown from "primevue/dropdown";
import { ref, computed, onMounted, onBeforeUnmount, inject } from "vue";
import { useToast } from "primevue/usetoast";

const apiClient = inject('axios');
const toast = useToast();

const isAnimating = ref(true);
const showLabels = ref(true);
const showHighTraffic = ref(false);
const selectedNode = ref(null);
const simulation = ref(null);
const nodes = ref([]);
const links = ref([]);
const loading = ref(false);
const selectedDemo = ref("/src/pcap_demos/connections/mesh_connections.json");
const rawData = ref([]);

const availableDemos = ref([
    {
        name: "Mesh Demo",
        path: "/src/pcap_demos/connections/mesh_connections.json",
        description: "Mesh-Topologie Demo Verbindungsdaten",
        type: "demo"
    },
    {
        name: "Ring Demo",
        path: "/src/pcap_demos/connections/ring_connections.json",
        description: "Ring-Topologie Demo Verbindungsdaten",
        type: "demo"
    },
    {
        name: "Star Demo",
        path: "/src/pcap_demos/connections/star_connections.json",
        description: "Stern-Topologie Demo Verbindungsdaten",
        type: "demo"
    },
    {
        name: "Tree Demo",
        path: "/src/pcap_demos/connections/tree_connections.json",
        description: "Baum-Topologie Demo Verbindungsdaten",
        type: "demo"
    },
]);

const svgRef = ref(null);
const linkElements = ref(null);
const nodeElements = ref(null);
const labelElements = ref(null);
const tooltip = ref(null);

const totalNodes = computed(() => nodes.value.length);
const totalConnections = computed(() => links.value.length);
const totalPackets = computed(() => rawData.value.reduce((sum, d) => sum + d.packets, 0));
const topConnections = computed(() => {
    return rawData.value
        .sort((a, b) => b.packets - a.packets)
        .slice(0, 5);
});
const topNodes = computed(() => {
    return nodes.value.sort((a, b) => b.total - a.total).slice(0, 5);
});

const loadSelectedDemo = async () => {
    loading.value = true;
    try {
        const isDatabasePcap = selectedDemo.value.startsWith('/pcap/');
        
                        if (isDatabasePcap) {
                    const pcapId = selectedDemo.value.split('/').pop(); 
                    const response = await apiClient.get(`/pcap/${pcapId}/connections`);
                    
                    if (response.data.status === 'success') {
                        rawData.value = response.data.connections;
                    } else {
                        throw new Error(response.data.message || 'Failed to load PCAP connections data');
                    }
        } else {
            // JSON demo files
            const resp = await fetch(selectedDemo.value);
            if (!resp.ok) throw new Error("Fehler beim Laden der Verbindungsdaten");
            const data = await resp.json();
            rawData.value = data;
        }
        
        processData();
        initGraph();
        
        toast.add({
            severity: "success",
            summary: "Verbindungsdaten geladen",
            detail: `${rawData.value.length} Verbindungen erfolgreich geladen.`,
            life: 3000,
        });
    } catch (e) {
        console.error("Fehler beim Laden der Verbindungsdaten:", e);
        rawData.value = [];
        processData();
        
        toast.add({
            severity: "error",
            summary: "Fehler",
            detail: "Verbindungsdaten konnten nicht geladen werden.",
            life: 5000,
        });
    } finally {
        loading.value = false;
    }
};



// Load PCAPs from database
const loadPcapsFromDatabase = async () => {
    try {
        const userId = localStorage.getItem('userId') || 'guest';
        
        const response = await apiClient.get(`/pcaps/${userId}`);
        const result = response.data;
        
        if (result.status === 'success' && result.pcaps) {
            const dbPcaps = result.pcaps.map(pcap => {
                const createdDate = pcap.created_at ? new Date(pcap.created_at) : new Date();
                const formattedDate = createdDate.toLocaleDateString('de-DE', {
                    year: 'numeric',
                    month: '2-digit',
                    day: '2-digit',
                    hour: '2-digit',
                    minute: '2-digit'
                });
                
                return {
                    name: pcap.topology_name || pcap.filename,
                    path: `/pcap/${pcap.id}`,
                    description: `Erstellt am ${formattedDate} - ${pcap.topology_type} Topologie mit ${pcap.node_count} Knoten`,
                    type: "saved",
                    isDatabase: true,
                    pcapId: pcap.id,
                    metadata: pcap.metadata_json ? JSON.parse(pcap.metadata_json) : null,
                    created_at: pcap.created_at,
                    hasConnectionsData: !!pcap.connections_json
                };
            });
            
            availableDemos.value = [...availableDemos.value, ...dbPcaps];
        }
    } catch (error) {
        console.error("Error loading PCAPs from database:", error);
    }
};

const initGraph = () => {
    // Clear previous visualization
    const svg = d3.select(svgRef.value);
    svg.selectAll("*").remove();

    const containerWidth = svgRef.value.parentElement.clientWidth;
    const width = Math.min(containerWidth - 40, 900);
    const height = 600;

    svg.attr("width", width)
        .attr("height", height)
        .attr("viewBox", [0, 0, width, height]);

    const g = svg.append("g");

    const zoom = d3
        .zoom()
        .scaleExtent([0.5, 3])
        .on("zoom", (event) => {
            g.attr("transform", event.transform);
        });

    svg.call(zoom);

    createTooltip();

    simulation.value = d3
        .forceSimulation(nodes.value)
        .force(
            "link",
            d3
                .forceLink(links.value)
                .id((d) => d.id)
                .distance((d) => getLinkDistance(d)),
        )
        .force(
            "charge",
            d3.forceManyBody().strength((d) => getNodeCharge(d)),
        )
        .force("center", d3.forceCenter(width / 2, height / 2))
        .force(
            "collision",
            d3.forceCollide().radius((d) => getNodeRadius(d) + 10),
        );

    createArrowMarkers(svg);

    linkElements.value = g
        .append("g")
        .attr("class", "links")
        .selectAll("line")
        .data(links.value)
        .join("line")
        .attr("class", "link")
        .attr("stroke", (d) => getLinkColor(d))
        .attr("stroke-width", (d) => getLinkWidth(d))
        .attr("stroke-opacity", 0.8)
        .attr("marker-end", "url(#arrowhead)")
        .on("mouseover", (event, d) => showLinkTooltip(event, d))
        .on("mouseout", () => hideTooltip());

    nodeElements.value = g
        .append("g")
        .attr("class", "nodes")
        .selectAll("circle")
        .data(nodes.value)
        .join("circle")
        .attr("class", "node")
        .attr("r", (d) => getNodeRadius(d))
        .attr("fill", (d) => getNodeColor(d))
        .attr("stroke", "#fff")
        .attr("stroke-width", 2)
        .style("filter", "drop-shadow(0 2px 4px rgba(0,0,0,0.1))")
        .on("mouseover", (event, d) => showNodeTooltip(event, d))
        .on("mouseout", () => hideTooltip())
        .on("click", (event, d) => selectNode(d))
        .call(
            d3
                .drag()
                .on("start", (event, d) => dragStarted(event, d))
                .on("drag", (event, d) => dragged(event, d))
                .on("end", (event, d) => dragEnded(event, d)),
        );

    labelElements.value = g
        .append("g")
        .attr("class", "labels")
        .selectAll("text")
        .data(nodes.value)
        .join("text")
        .attr("class", "label")
        .attr("text-anchor", "middle")
        .attr("dy", (d) => getNodeRadius(d) + 16)
        .attr("font-size", "11px")
        .attr("font-weight", "500")
        .attr("fill", "#374151")
        .text((d) => d.id)
        .style("pointer-events", "none")
        .style("display", showLabels.value ? "block" : "none");

    simulation.value.on("tick", () => {
        linkElements.value
            .attr("x1", (d) => d.source.x)
            .attr("y1", (d) => d.source.y)
            .attr("x2", (d) => d.target.x)
            .attr("y2", (d) => d.target.y);

        nodeElements.value.attr("cx", (d) => d.x).attr("cy", (d) => d.y);

        labelElements.value.attr("x", (d) => d.x).attr("y", (d) => d.y);
    });
};

const processData = () => {
    let filteredData = rawData.value;

    if (showHighTraffic.value) {
        filteredData = filteredData.filter((d) => d.packets > 20);
    }

    const nodeIds = new Set([
        ...filteredData.map((d) => d.source),
        ...filteredData.map((d) => d.destination),
    ]);

    nodes.value = Array.from(nodeIds).map((id) => ({ id }));

    const nodeTotals = {};
    filteredData.forEach((d) => {
        nodeTotals[d.source] = (nodeTotals[d.source] || 0) + d.packets;
        nodeTotals[d.destination] =
            (nodeTotals[d.destination] || 0) + d.packets;
    });

    nodes.value.forEach((node) => {
        node.total = nodeTotals[node.id] || 0;
    });

    links.value = filteredData.map((d) => ({
        source: d.source,
        target: d.destination,
        value: d.packets,
    }));
};

const createTooltip = () => {
    tooltip.value = d3
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
};

const createArrowMarkers = (svg) => {
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
};

const getNodeRadius = (d) => {
    return Math.max(8, Math.sqrt(d.total) * 0.8 + 4);
};

const getNodeColor = (d) => {
    if (d.id.startsWith("224.")) {
        return "#f59e0b"; // Multicast - amber
    }
    return "#6366f1"; // Regular - indigo
};

const getNodeCharge = (d) => {
    return d.id.startsWith("224.") ? -800 : -400;
};

const getLinkDistance = (d) => {
    return d.value > 50 ? 80 : 120;
};

const getLinkWidth = (d) => {
    return Math.max(1, Math.sqrt(d.value) * 0.3);
};

const getLinkColor = (d) => {
    if (d.value > 50) return "#dc2626"; // High traffic - red
    if (d.value > 20) return "#f59e0b"; // Medium traffic - amber
    return "#6b7280"; // Low traffic - gray
};

const showNodeTooltip = (event, d) => {
    tooltip.value.style("visibility", "visible").html(`
            <div><strong>${d.id}</strong></div>
            <div>Gesamte Pakete: ${d.total}</div>
            <div>Typ: ${d.id.startsWith("224.") ? "Multicast" : "Standard"}</div>
        `);
    moveTooltip(event);
};

const showLinkTooltip = (event, d) => {
    tooltip.value.style("visibility", "visible").html(`
            <div><strong>Verbindung</strong></div>
            <div>Von: ${d.source.id}</div>
            <div>Zu: ${d.target.id}</div>
            <div>Pakete: ${d.value}</div>
        `);
    moveTooltip(event);
};

const hideTooltip = () => {
    tooltip.value.style("visibility", "hidden");
};

const moveTooltip = (event) => {
    tooltip.value
        .style("top", event.pageY - 10 + "px")
        .style("left", event.pageX + 10 + "px");
};

const selectNode = (d) => {
    selectedNode.value = d;

    linkElements.value
        .attr("stroke-opacity", (link) =>
            link.source.id === d.id || link.target.id === d.id
                ? 1
                : 0.3,
        )
        .attr("stroke-width", (link) =>
            link.source.id === d.id || link.target.id === d.id
                ? getLinkWidth(link) + 1
                : getLinkWidth(link),
        );

    nodeElements.value
        .attr("stroke", (node) => (node.id === d.id ? "#000" : "#fff"))
        .attr("stroke-width", (node) => (node.id === d.id ? 3 : 2));
};

const resetLayout = () => {
    if (simulation.value) {
        simulation.value.alpha(1).restart();
    }
};

const centerGraph = () => {
    const svg = d3.select(svgRef.value);

    svg.transition()
        .duration(750)
        .call(
            d3.zoom().transform,
            d3.zoomIdentity.translate(0, 0).scale(1),
        );
};

const updateVisualization = () => {
    initGraph();
};

const updateLabels = () => {
    if (labelElements.value) {
        labelElements.value.style(
            "display",
            showLabels.value ? "block" : "none",
        );
    }
};

const handleResize = () => {
    clearTimeout(resizeTimeout.value);
    resizeTimeout.value = setTimeout(() => {
        initGraph();
    }, 300);
};

const dragStarted = (event, d) => {
    if (!event.active) simulation.value.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
};

const dragged = (event, d) => {
    d.fx = event.x;
    d.fy = event.y;
};

const dragEnded = (event, d) => {
    if (!event.active) simulation.value.alphaTarget(0);
    d.fx = null;
    d.fy = null;
};

// Lifecycle hooks
onMounted(async () => {
    await loadPcapsFromDatabase();
    
    if (availableDemos.value.length > 0) {
        selectedDemo.value = availableDemos.value[0].path;
    }
    
    await loadSelectedDemo();
    window.addEventListener("resize", handleResize);
});

onBeforeUnmount(() => {
    d3.select("body").selectAll(".tooltip").remove();
    window.removeEventListener("resize", handleResize);
    if (simulation.value) {
        simulation.value.stop();
    }
});

const resizeTimeout = ref(null);
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

/* PCAP Selection Styles */
.pcap-selection {
    display: flex;
    align-items: center;
}

.pcap-label {
    font-weight: 600;
    color: var(--nlb-text-primary);
    font-size: 0.875rem;
    white-space: nowrap;
}

.pcap-dropdown {
    min-width: 250px;
}

.pcap-dropdown :deep(.p-dropdown) {
    background: var(--nlb-bg-primary);
    border: 2px solid var(--nlb-border-light);
    border-radius: 12px;
    padding: 0.5rem 1rem;
    transition: all 0.2s ease;
}

.pcap-dropdown :deep(.p-dropdown:hover) {
    border-color: var(--nlb-primary);
}

.pcap-dropdown :deep(.p-dropdown:focus) {
    border-color: var(--nlb-primary);
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.pcap-dropdown :deep(.p-dropdown-label) {
    color: var(--nlb-text-primary);
    font-weight: 500;
}

.pcap-dropdown :deep(.p-dropdown-trigger) {
    color: var(--nlb-text-secondary);
}

.pcap-option {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}

.pcap-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.pcap-name {
    font-weight: 600;
    color: var(--nlb-text-primary);
}

.pcap-badge {
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--nlb-text-light);
    background-color: var(--nlb-primary);
}

.pcap-badge.demo {
    background-color: var(--nlb-warning);
}

.pcap-description {
    font-size: 0.8rem;
    color: var(--nlb-text-secondary);
}

/* Loading state for dropdown */
.pcap-dropdown :deep(.p-dropdown.p-component.p-disabled) {
    opacity: 0.6;
    cursor: not-allowed;
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
    flex-direction: row;
    justify-content: flex-start;
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
