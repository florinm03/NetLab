<template>
    <div class="lab-controller-container">
        <!-- Main Header -->
        <div class="header-section">
            <h1 class="page-title">Topologie Erstellen</h1>
            <p class="page-description">
                Netzwerktopologien effizient erstellen und verwalten
            </p>
        </div>

        <!-- Progress Indicator -->
        <div class="progress-section">
            <div class="progress-header">
                <h3>Einrichtungsfortschritt</h3>
                <div class="progress-steps">
                    <div
                        :class="[
                            'progress-step',
                            {
                                active: parseInt(activeStep) >= 1,
                                completed: parseInt(activeStep) > 1,
                            },
                        ]"
                    >
                        <div class="step-circle">1</div>
                        <span>Topologie auswählen</span>
                    </div>
                    <div
                        class="progress-line"
                        :class="{ completed: parseInt(activeStep) > 1 }"
                    ></div>
                    <div
                        :class="[
                            'progress-step',
                            {
                                active: parseInt(activeStep) >= 2,
                                completed: parseInt(activeStep) > 2,
                            },
                        ]"
                    >
                        <div class="step-circle">2</div>
                        <span>Konfigurieren</span>
                    </div>
                    <div
                        class="progress-line"
                        :class="{ completed: parseInt(activeStep) > 2 }"
                    ></div>
                    <div
                        :class="[
                            'progress-step',
                            { active: parseInt(activeStep) >= 3 },
                        ]"
                    >
                        <div class="step-circle">3</div>
                        <span>Deployment</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- Main Content Card -->
        <div class="main-card">
            <Stepper v-model:value="activeStep" linear orientation="vertical">
                <StepItem value="1">
                    <Step value="1">
                        <i class="pi pi-search step-icon"></i>
                        Wähle eine Topologie aus
                    </Step>
                    <StepPanel value="1">
                        <div class="step-content">
                            <div class="step-header">
                                <h3>Selektion der Netzwerktopologie</h3>
                                <p>
                                    Wählen Sie die Netzwerktopologie, die Ihren Testanforderungen am besten entspricht.
                                </p>
                            </div>

                            <div class="topology-selection-card">
                                <div class="selection-header">
                                    <i class="pi pi-sitemap"></i>
                                    <h4>Verfügbare Topologien</h4>
                                </div>

                                <Select
                                    v-model="selectedTopology"
                                    :options="topologies"
                                    optionLabel="name"
                                    placeholder="Wähle eine Topologie"
                                    class="topology-select"
                                >
                                    <template #footer>
                                        <div class="select-footer">
                                            <Button
                                                label="Benutzerdefinierte Topologie erstellen"
                                                fluid
                                                severity="secondary"
                                                text
                                                size="small"
                                                icon="pi pi-plus"
                                            />
                                        </div>
                                    </template>
                                </Select>

                                <div
                                    v-if="selectedTopology"
                                    class="topology-info"
                                >
                                    <div class="info-card">
                                        <i class="pi pi-info-circle"></i>
                                        <div>
                                            <strong
                                                >Ausgewählt:
                                                {{
                                                    selectedTopology.name
                                                }}</strong
                                            >
                                            <p>
                                                Diese Topologie wird im nächsten Schritt konfiguriert.
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div class="step-actions">
                                <Button
                                    label="Weiter zur Konfiguration"
                                    icon="pi pi-arrow-right"
                                    @click="nextStep"
                                    :disabled="!selectedTopology"
                                    class="primary-button"
                                />
                            </div>
                        </div>
                    </StepPanel>
                </StepItem>

                <StepItem value="2">
                    <Step value="2">
                        <i class="pi pi-cog step-icon"></i>
                        Konfiguriere die Topologie
                    </Step>
                    <StepPanel value="2">
                        <div class="step-content">
                            <div class="step-header">
                                <h3>Topologiekonfiguration</h3>
                                <p>
                                    Richten Sie Ihre Netzwerkumgebung ein und erstellen Sie Ihre Topologie.
                                </p>
                            </div>

                            <div class="config-grid">
                                <!-- Topology Management Card -->
                                <div class="config-card primary-card">
                                    <div class="card-header">
                                        <i class="pi pi-network"></i>
                                        <h4>Topologie Management</h4>
                                    </div>
                                    <div class="card-content">
                                        <Button
                                            label="Topologie erstellen"
                                            icon="pi pi-plus-circle"
                                            @click="createTopology"
                                            :loading="isLoading"
                                            class="action-button primary"
                                        />
                                        <Button
                                            label="Aktive Nodes abfragen"
                                            icon="pi pi-refresh"
                                            @click="getOwnNodes"
                                            class="action-button secondary"
                                        />
                                    </div>
                                </div>

                                <!-- Status Card -->
                                <div class="config-card status-card">
                                    <div class="card-header">
                                        <i class="pi pi-chart-line"></i>
                                        <h4>System Status</h4>
                                    </div>
                                    <div class="card-content">
                                        <div class="status-item">
                                            <span class="status-label">Topologie:</span>
                                            <span class="status-value">{{ selectedTopology?.name || 'Nicht ausgewählt' }}</span>
                                        </div>
                                        <div class="status-item">
                                            <span class="status-label">Aktive Nodes:</span>
                                            <span class="status-value">{{ ownNodes.length }}</span>
                                        </div>
                                        <div class="status-item">
                                            <span class="status-label">Status:</span>
                                            <span class="status-value" :class="ownNodes.length > 0 ? 'status-active' : 'status-inactive'">
                                                {{ ownNodes.length > 0 ? 'Aktiv' : 'Inaktiv' }}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Topology Graph -->
                            <div
                                v-if="ownNodes.length > 0"
                                class="topology-graph-section"
                            >
                                <TopologyGraph
                                    :nodes="graphNodes"
                                    :connections="graphConnections"
                                    @node-click="onNodeClick"
                                    @clear-all="clearAllNodes"
                                />
                            </div>

                            <!-- Current Nodes Info -->
                            <div
                                v-if="ownNodes.length > 0"
                                class="nodes-info-card"
                            >
                                <div class="nodes-header">
                                    <i class="pi pi-sitemap"></i>
                                    <h4>Aktive Netzwerkknoten</h4>
                                    <div class="node-count">
                                        {{ ownNodes.length }} Knoten
                                    </div>
                                </div>
                                
                                <!-- Topology Connections Overview -->
                                <div class="topology-overview">
                                    <h5>Topologie: {{ selectedTopology?.name }}</h5>
                                    <div class="connections-info">
                                        <span>{{ graphConnections.length }} Verbindungen</span>
                                    </div>
                                </div>
                                
                                <div class="nodes-grid">
                                    <div
                                        v-for="(node, index) in ownNodes"
                                        :key="index"
                                        class="node-item"
                                        @mouseenter="onNodeHover($event, node, index)"
                                        @mouseleave="onNodeOut"
                                    >
                                        <div class="node-content">
                                            <i class="pi pi-circle-fill node-indicator"></i>
                                            <span class="node-name">{{
                                            node.name || `Knoten ${index + 1}`
                                        }}</span>
                                            <div class="node-actions">
                                                <Button 
                                                    class="terminal-button"
                                                    @click="openNodeTerminal(node)"
                                                    text 
                                                    size="small"
                                                    severity="secondary"
                                                    title="Terminal öffnen"
                                                >
                                                    <i class="pi pi-terminal"></i>
                                                    <i class="pi pi-arrow-up-right arrow-icon"></i>
                                                </Button>
                                                <Button 
                                                    icon="pi pi-trash" 
                                                    @click="deleteNode(node)"
                                                    text 
                                                    size="small"
                                                    severity="danger"
                                                    title="Knoten löschen"
                                                />
                                            </div>
                                        </div>
                                        
                                        <!-- Node Connections -->
                                        <div class="node-connections">
                                            <span class="connections-label">Verbindungen:</span>
                                            <div class="connection-list">
                                                <span 
                                                    v-for="connection in getNodeConnections(node, index)"
                                                    :key="connection.target"
                                                    class="connection-item"
                                                >
                                                    → {{ getNodeName(connection.target) }}
                                                </span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                
                                <!-- Hover Tooltip for Routing Table -->
                                <div 
                                    v-if="hoveredNode" 
                                    class="routing-tooltip"
                                    :style="{ left: tooltipPosition.x + 'px', top: tooltipPosition.y + 'px' }"
                                >
                                    <div class="tooltip-header">
                                        <h6>{{ hoveredNode.name || `Knoten ${hoveredNodeIndex + 1}` }}</h6>
                                        <Button 
                                            icon="pi pi-times" 
                                            @click="hoveredNode = null" 
                                            text 
                                            size="small"
                                            class="tooltip-close"
                                        />
                                    </div>
                                    
                                    <div class="routing-table">
                                        <h6>Routing Tabelle (netstat -r)</h6>
                                        <div class="table-container">
                                            <table class="route-table">
                                                <thead>
                                                    <tr>
                                                        <th>Ziel</th>
                                                        <th>Gateway</th>
                                                        <th>Genmask</th>
                                                        <th>Flags</th>
                                                        <th>Iface</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    <tr v-for="route in hoveredNode.routes" :key="route.destination">
                                                        <td>{{ route.destination }}</td>
                                                        <td>{{ route.gateway }}</td>
                                                        <td>{{ route.genmask }}</td>
                                                        <td>{{ route.flags }}</td>
                                                        <td>{{ route.iface }}</td>
                                                    </tr>
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div v-else-if="!isLoading" class="empty-state">
                                <i class="pi pi-info-circle"></i>
                                <h4>Keine aktiven Nodes</h4>
                                <p>
                                    Klicken Sie auf "Topologie erstellen", um Ihr Netzwerk aufzubauen.
                                </p>
                            </div>

                            <div class="step-actions">
                                <Button
                                    label="Zurück"
                                    icon="pi pi-arrow-left"
                                    severity="secondary"
                                    @click="previousStep"
                                />
                                <Button
                                    label="Weiter zur Bereitstellung"
                                    icon="pi pi-arrow-right"
                                    @click="nextStep"
                                    :disabled="ownNodes.length === 0"
                                    class="primary-button"
                                />
                            </div>
                        </div>
                    </StepPanel>
                </StepItem>

                <StepItem value="3">
                    <Step value="3">
                        <i class="pi pi-cloud step-icon"></i>
                        Bereitstellen der Topologie
                    </Step>
                    <StepPanel value="3">
                        <div class="step-content">
                            <div class="step-header">
                                <h3>Topologiebereitstellung</h3>
                                <p>
                                    Greifen Sie auf Ihre bereitgestellten Netzwerkknoten zu und verwalten Sie sie.
                                </p>
                            </div>

                            <div class="deployment-info">
                                <div class="deployment-stats">
                                    <div class="stat-item">
                                        <i class="pi pi-server"></i>
                                        <div>
                                            <span class="stat-number">{{
                                                terminal_urls.length
                                            }}</span>
                                            <span class="stat-label"
                                                >Aktive Nodes</span
                                            >
                                        </div>
                                    </div>
                                    <div class="stat-item">
                                        <i class="pi pi-check-circle"></i>
                                        <div>
                                            <span class="stat-number">{{
                                                selectedTopology?.name || "N/A"
                                            }}</span>
                                            <span class="stat-label"
                                                >Topologie Typ</span
                                            >
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div
                                v-if="terminal_urls.length > 0"
                                class="terminals-section"
                            >
                                <div class="terminals-header">
                                    <h4>Knoten Terminals</h4>
                                    <p>
                                        Klicken Sie auf einen beliebigen Knoten, um auf dessen Terminalschnittstelle zuzugreifen.
                                    </p>
                                </div>

                                <Accordion
                                    :multiple="true"
                                    v-model:activeIndex="activeIndexes"
                                    class="node-accordion"
                                >
                                    <AccordionTab
                                        v-for="(node, index) in terminal_urls"
                                        :key="index"
                                    >
                                        <template #header>
                                            <div class="accordion-header">
                                                <i class="pi pi-desktop"></i>
                                                <span
                                                    >Knoten {{ index + 1 }}</span
                                                >
                                                <div class="node-status online">
                                                    Online
                                                </div>
                                            </div>
                                        </template>

                                        <div class="terminal-wrapper">
                                            <div class="terminal-info">
                                                <p>
                                                    Terminalzugang für Knoten
                                                    {{ index + 1 }}
                                                </p>
                                            </div>
                                            <iframe
                                                :src="node.url"
                                                class="terminal-iframe"
                                                :title="`Container Terminal ${index + 1}`"
                                                sandbox="allow-same-origin allow-scripts allow-forms allow-popups"
                                                @load="onIframeLoad"
                                                @error="onIframeError"
                                            ></iframe>
                                        </div>
                                    </AccordionTab>
                                </Accordion>
                            </div>

                            <div v-else class="empty-state">
                                <i class="pi pi-info-circle"></i>
                                <h4>Keine Knoten verfügbar</h4>
                                <p>
                                    Bitte gehen Sie zurück und erstellen Sie Ihre Topologie zuerst.
                                </p>
                            </div>

                            <div class="step-actions">
                                <Button
                                    label="Zurück"
                                    icon="pi pi-arrow-left"
                                    severity="secondary"
                                    @click="previousStep"
                                />
                                <Button
                                    label="Prozess Neustarten"
                                    icon="pi pi-refresh"
                                    severity="secondary"
                                    @click="resetStepper"
                                />
                            </div>
                        </div>
                    </StepPanel>
                </StepItem>
            </Stepper>
        </div>
    </div>
</template>

<script>
import { computed } from "vue";
import { useStore } from "vuex";
import { ref } from "vue";
import Select from "primevue/select";
import Button from "primevue/button";
import Stepper from "primevue/stepper";
import StepList from "primevue/steplist";
import StepPanels from "primevue/steppanels";
import StepItem from "primevue/stepitem";
import Step from "primevue/step";
import StepPanel from "primevue/steppanel";
import Dropdown from "primevue/dropdown";
import Accordion from "primevue/accordion";
import AccordionPanel from "primevue/accordionpanel";
import AccordionHeader from "primevue/accordionheader";
import AccordionContent from "primevue/accordioncontent";
import AccordionTab from "primevue/accordiontab";
import { ButtonGroup } from "primevue";
import { useToast } from "primevue/usetoast";
import TopologyGraph from "./TopologyGraph.vue";

export default {
    created() {
        this.$store.dispatch("initializeUser");
    },
    setup() {
        const toast = useToast();
        return { toast };
    },
    computed: {
        userId() {
            return this.$store.state.user.id;
        },
    },
    name: "LabController",
    components: {
        Select,
        Button,
        Stepper,
        Step,
        StepList,
        Dropdown,
        StepPanels,
        StepItem,
        StepPanel,
        Accordion,
        AccordionHeader,
        AccordionTab,
        AccordionPanel,
        AccordionContent,
        TopologyGraph,
    },
    data() {
        return {
            isLoading: false,
            selectedTopology: null,
            activeStep: "1",
            topologies: [
                { name: "Mini-Ring", code: "mini_ring" },
                { name: "Ring", code: "ring" },
                { name: "Mesh", code: "mesh" },
                { name: "Tree", code: "tree" },
                { name: "Star", code: "star" },
            ],
            activeIndexes: [0, 2],
            ownNodes: [],
            node_urls: [],
            terminal_urls: [],
            graphNodes: [],
            graphConnections: [],
            hoveredNode: null,
            hoveredNodeIndex: null,
            tooltipPosition: { x: 0, y: 0 },
        };
    },
    watch: {
        // activeStep(newVal) {
        //     if (parseInt(newVal) === 2) {
        //         this.getOwnNodes();
        //         this.startAutoRefresh();
        //     } else {
        //         this.stopAutoRefresh();
        //     }
        // },
    },
    // beforeUnmount() {
    //     this.stopAutoRefresh();
    // },
    methods: {
        async nextStep() {
            console.log("selectedTopology", this.selectedTopology);
            const currentStep = parseInt(this.activeStep);
            if (currentStep < 3) {
                this.activeStep = String(currentStep + 1);

                // Automatically fetch nodes when entering step 2
                if (currentStep + 1 === 2) {
                    await this.getOwnNodes();
                }
            }
        },

        previousStep() {
            const currentStep = parseInt(this.activeStep);
            if (currentStep > 1) {
                this.activeStep = String(currentStep - 1);
            }
        },

        resetStepper() {
            this.activeStep = "1";
            this.selectedTopology = null;
            this.isLoading = false;
        },
        // startAutoRefresh() {
        //     this.refreshInterval = setInterval(() => {
        //         this.getOwnNodes();
        //     }, 1000);
        // },



        getStepHeader(stepNumber, label, icon) {
            return {
                value: label,
                icon: icon,
                number: stepNumber,
            };
        },

        async createTopology() {
            const userId = this.userId;
            console.log("selectedTopology.value:", this.selectedTopology.code);

            try {
                const response = await this.$axios.post("/start-topology", {
                    user_id: userId,
                    topology: this.selectedTopology.code || "star",
                });

                console.log("Topology created:", response.data);

                if (response.data.status === "success") {
                    // await checkStatus();
                } else {
                    console.log(
                        response.data.message || "Failed to create topology",
                    );
                }
            } catch (err) {
            } finally {
            }
        },

        async getOwnNodes() {
            try {
                this.isLoading = true;
                const userId = this.userId;

                const response = await this.$axios.get(
                    `/user-topologies/${userId}`,
                );

                if (response.data.status === "success") {
                    this.ownNodes = response.data.nodes;
                    this.updateGraphData(); // Update graph data when nodes change
                    console.log("data :", JSON.stringify(response));

                    const terminal_urls_response = await this.$axios.get(
                        "/ttyd/getOwnNodes",
                        {
                            params: { user_id: userId },
                        },
                    );

                    if (terminal_urls_response.data.status === "success") {
                        this.node_urls = response.data.nodes;
                        console.log(
                            "node_urls :",
                            JSON.stringify(this.node_urls),
                        );
                        console.log(
                            "terminal_urls_response :",
                            JSON.stringify(terminal_urls_response),
                        );
                        this.terminal_urls =
                            terminal_urls_response.data.terminals;
                    } else {
                        console.log(
                            "error getting nodes :",
                            JSON.stringify(terminal_urls_response),
                        );
                    }
                } else {
                    console.log(
                        "error getting nodes :",
                        JSON.stringify(response),
                    );
                }
            } catch (err) {
                console.error("Error fetching nodes:", err);
            } finally {
                this.isLoading = false;
            }
        },

        // Graph-related methods
        updateGraphData() {
            // Convert ownNodes to graph format
            this.graphNodes = this.ownNodes.map((node, index) => ({
                id: node.name || `node-${index}`,
                name: node.name || `Knoten ${index + 1}`,
                ip: node.ip || `172.16.0.${index + 1}`,
                status: 'online',
                type: 'router'
            }));

            // Generate connections based on topology type
            this.graphConnections = this.generateConnections();
        },

        generateConnections() {
            const connections = [];
            const nodeCount = this.graphNodes.length;

            if (this.selectedTopology?.code === 'ring') {
                // Ring topology: each node connects to next and previous
                for (let i = 0; i < nodeCount; i++) {
                    const next = (i + 1) % nodeCount;
                    connections.push({
                        source: this.graphNodes[i].id,
                        target: this.graphNodes[next].id,
                        type: 'ethernet'
                    });
                }
            } else if (this.selectedTopology?.code === 'mesh') {
                // Mesh topology: each node connects to all others
                for (let i = 0; i < nodeCount; i++) {
                    for (let j = i + 1; j < nodeCount; j++) {
                        connections.push({
                            source: this.graphNodes[i].id,
                            target: this.graphNodes[j].id,
                            type: 'ethernet'
                        });
                    }
                }
            } else if (this.selectedTopology?.code === 'star') {
                // Star topology: central node connects to all others
                if (nodeCount > 1) {
                    const centralNode = this.graphNodes[0];
                    for (let i = 1; i < nodeCount; i++) {
                        connections.push({
                            source: centralNode.id,
                            target: this.graphNodes[i].id,
                            type: 'ethernet'
                        });
                    }
                }
            } else if (this.selectedTopology?.code === 'tree') {
                // Tree topology: hierarchical structure
                for (let i = 1; i < nodeCount; i++) {
                    const parentIndex = Math.floor((i - 1) / 2);
                    if (parentIndex < nodeCount) {
                        connections.push({
                            source: this.graphNodes[parentIndex].id,
                            target: this.graphNodes[i].id,
                            type: 'ethernet'
                        });
                    }
                }
            } else {
                // Default: mini-ring or custom
                for (let i = 0; i < nodeCount - 1; i++) {
                    connections.push({
                        source: this.graphNodes[i].id,
                        target: this.graphNodes[i + 1].id,
                        type: 'ethernet'
                    });
                }
            }

            return connections;
        },

        onNodeClick(node) {
            console.log('Node clicked:', node);
            // You can add additional functionality here
        },

        async onNodeHover(event, node, index) {
            this.hoveredNode = {
                ...node,
                routes: await this.fetchRoutingTable(node)
            };
            this.hoveredNodeIndex = index;
            
            this.tooltipPosition = {
                x: event.pageX + 10,
                y: event.pageY - 10
            };
        },

        onNodeOut() {
            this.hoveredNode = null;
            this.hoveredNodeIndex = null;
        },

        async fetchRoutingTable(node) {
            try {
                // Fetch real routing table from backend
                const response = await this.$axios.get(`/node-routing/${node.name}`);
                if (response.data.status === 'success') {
                    return response.data.routes;
                }
            } catch (error) {
                console.error('Error fetching routing table:', error);
            }
            
            // Fallback to mock data
            return this.generateMockRoutingTable(node);
        },

        generateMockRoutingTable(node) {
            return [
                {
                    destination: 'default',
                    gateway: '172.16.0.1',
                    genmask: '0.0.0.0',
                    flags: 'UG',
                    iface: 'eth0'
                },
                {
                    destination: '172.16.0.0',
                    gateway: '0.0.0.0',
                    genmask: '255.255.0.0',
                    flags: 'U',
                    iface: 'eth0'
                },
                {
                    destination: '192.168.1.0',
                    gateway: '172.16.0.2',
                    genmask: '255.255.255.0',
                    flags: 'UG',
                    iface: 'eth0'
                }
            ];
        },

        getNodeConnections(node, index) {
            return this.graphConnections.filter(conn => 
                conn.source === node.name || conn.target === node.name
            );
        },

        getNodeName(nodeId) {
            const node = this.ownNodes.find(n => n.name === nodeId);
            return node ? node.name : nodeId;
        },

        async deleteNode(node) {
            try {
                const userId = this.userId;
                const response = await this.$axios.delete(`/delete-node/${userId}/${node.id}`);
                
                if (response.data.status === 'success') {
                    // Remove node from local data
                    this.ownNodes = this.ownNodes.filter(n => n.name !== node.name);
                    this.updateGraphData();
                    
                    // Show success message
                    this.toast.add({
                        severity: 'success',
                        summary: 'Knoten gelöscht',
                        detail: `Knoten "${node.name}" wurde erfolgreich entfernt`,
                        life: 3000
                    });
                }
            } catch (error) {
                console.error('Error deleting node:', error);
                this.toast.add({
                    severity: 'error',
                    summary: 'Fehler',
                    detail: 'Knoten konnte nicht gelöscht werden',
                    life: 3000
                });
            }
        },

        openNodeTerminal(node) {
            // Use the same logic as in the deployment section
            // Find the node index in ownNodes and use the same index for terminal_urls
            const nodeIndex = this.ownNodes.findIndex(n => n.name === node.name);
            
            if (nodeIndex >= 0 && this.terminal_urls[nodeIndex] && this.terminal_urls[nodeIndex].url) {
                console.log(`Opening terminal for node: ${node.name}`, this.terminal_urls[nodeIndex]);
                window.open(this.terminal_urls[nodeIndex].url, '_blank');
            } else {
                console.error(`No terminal URL found for node: ${node.name}`);
                console.log('Node index:', nodeIndex);
                console.log('Available terminals:', this.terminal_urls);
                console.log('Available nodes:', this.ownNodes);
                
                this.toast.add({
                    severity: 'error',
                    summary: 'Terminal nicht verfügbar',
                    detail: `Terminal für Knoten "${node.name}" konnte nicht gefunden werden`,
                    life: 3000
                });
            }
        },

        async clearAllNodes() {
            try {
                const userId = this.userId;
                const response = await this.$axios.delete(`/clear-topology/${userId}`);
                
                if (response.data.status === 'success') {
                    this.ownNodes = [];
                    this.graphNodes = [];
                    this.graphConnections = [];
                    this.terminal_urls = [];
                    
                    this.toast.add({
                        severity: 'success',
                        summary: 'Topologie gelöscht',
                        detail: 'Alle Knoten wurden erfolgreich entfernt',
                        life: 3000
                    });
                }
            } catch (error) {
                console.error('Error clearing topology:', error);
                this.toast.add({
                    severity: 'error',
                    summary: 'Fehler',
                    detail: 'Topologie konnte nicht gelöscht werden',
                    life: 3000
                });
            }
        },


    },
};
</script>

<style scoped>
/* Container and Layout */
.lab-controller-container {
    width: 100%;
    margin: 0 auto;
    padding: 20px;
    background: var(--nlb-gradient-secondary);
    height: auto;
}

/* Main Header */
.main-header {
    background: var(--nlb-gradient-primary);
    border-radius: 16px;
    margin-bottom: 24px;
    box-shadow: 0 8px 32px var(--nlb-primary);
}

.header-content {
    padding: 32px;
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    color: white;
}

.header-left {
    display: flex;
    flex-direction: row;
    align-items: center;
    gap: 20px;
}

.header-icon {
    font-size: 2.5rem;
    opacity: 0.9;
}

.header-left h1 {
    margin: 0;
    font-size: 2.2rem;
    font-weight: 700;
    background: linear-gradient(45deg, var(--nlb-text-light), var(--nlb-primary-light));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.header-subtitle {
    margin: 8px 0 0 0;
    opacity: 0.8;
    font-size: 1.1rem;
}
.header-section {
    text-align: center;
    margin-bottom: 3rem;
}

.page-title {
    font-size: 2.5rem;
    font-weight: 700;
    color: var(--nlb-text-primary);
    margin-bottom: 0.5rem;
}

.page-description {
    font-size: 1.1rem;
    color: var(--nlb-text-secondary);
    margin: 0;
}
.user-info {
    display: flex;
    align-items: center;
    gap: 8px;
    background: var(--nlb-bg-muted);
    padding: 12px 16px;
    border-radius: 12px;
    backdrop-filter: blur(10px);
}

/* Progress Section */
.progress-section {
    background: var(--nlb-bg-primary);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 24px;
    box-shadow: 0 4px 20px var(--nlb-border-medium);
}

.progress-header h3 {
    margin: 0 0 20px 0;
    color: var(--nlb-text-primary);
    font-weight: 600;
}

.progress-steps {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 20px;
}

.progress-step {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    opacity: 0.5;
    transition: all 0.3s ease;
}

.progress-step.active,
.progress-step.completed {
    opacity: 1;
}

.step-circle {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: var(--nlb-border-light);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    transition: all 0.3s ease;
}

.progress-step.active .step-circle {
    background: var(--nlb-primary);
    color: var(--nlb-text-light);
}

.progress-step.completed .step-circle {
    background: var(--nlb-success);
    color: var(--nlb-text-light);
}

.progress-line {
    width: 60px;
    height: 2px;
    background: var(--nlb-border-light);
    transition: all 0.3s ease;
}

.progress-line.completed {
    background: var(--nlb-success);
}

/* Main Card */
.main-card {
    background: var(--nlb-bg-primary);
    border-radius: 16px;
    padding: 32px;
    box-shadow: 0 4px 20px var(--nlb-border-medium);
}

/* Step Content */
.step-content {
    padding: 24px 0;
}

.step-header {
    margin-bottom: 32px;
    text-align: center;
}

.step-header h3 {
    margin: 0 0 8px 0;
    color: var(--nlb-text-primary);
    font-size: 1.8rem;
    font-weight: 600;
}

.step-header p {
    margin: 0;
    color: var(--nlb-text-secondary);
    font-size: 1.1rem;
}

.step-icon {
    margin-right: 12px;
    font-size: 1.2rem;
}

/* Topology Selection */
.topology-selection-card {
    background: var(--nlb-bg-secondary);
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 32px;
}

.selection-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 20px;
}

.selection-header h4 {
    margin: 0;
    color: var(--nlb-text-primary);
    font-weight: 600;
}

.topology-select {
    width: 100%;
    margin-bottom: 16px;
}

.select-footer {
    padding: 16px;
}

.topology-info {
    margin-top: 16px;
}

.info-card {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    background: var(--nlb-info-light);
    border: 1px solid var(--nlb-info);
    border-radius: 8px;
    padding: 16px;
}

.info-card i {
    color: var(--nlb-info-dark);
    margin-top: 2px;
}

.info-card strong {
    color: var(--nlb-text-primary);
}

.info-card p {
    margin: 4px 0 0 0;
    color: var(--nlb-text-secondary);
}

/* Configuration Grid */
.config-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 24px;
    margin-bottom: 32px;
}

.config-card {
    background: var(--nlb-bg-secondary);
    border-radius: 12px;
    padding: 24px;
    border: 1px solid var(--nlb-border-light);
    transition: all 0.3s ease;
}

.config-card.primary-card {
    background: var(--nlb-bg-primary);
    border: 1px solid var(--nlb-border-light);
    box-shadow: 0 4px 20px var(--nlb-border-medium);
}

.config-card.status-card {
    background: var(--nlb-bg-primary);
    border: 1px solid var(--nlb-border-light);
    box-shadow: 0 4px 20px var(--nlb-border-medium);
}

.card-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 20px;
    padding-bottom: 16px;
    border-bottom: 1px solid var(--nlb-border-light);
}

.card-header h4 {
    margin: 0;
    color: var(--nlb-text-primary);
    font-weight: 600;
}

.card-content {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.status-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid var(--nlb-border-light);
}

.status-item:last-child {
    border-bottom: none;
}

.status-label {
    font-weight: 600;
    color: var(--nlb-text-secondary);
}

.status-value {
    font-weight: 600;
    color: var(--nlb-text-primary);
}

.status-value.status-active {
    color: var(--nlb-success-dark);
}

.status-value.status-inactive {
    color: var(--nlb-error-dark);
}



/* Topology Graph Section */
.topology-graph-section {
    margin-top: 20px;
    margin-bottom: 20px;
}

/* Topology Overview */
.topology-overview {
    background: var(--nlb-bg-secondary);
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 20px;
    border: 1px solid var(--nlb-border-light);
}

.topology-overview h5 {
    margin: 0 0 8px 0;
    color: var(--nlb-text-primary);
    font-weight: 600;
}

.connections-info {
    color: var(--nlb-text-secondary);
    font-size: 0.9rem;
}

/* Nodes Info */
.nodes-info-card {
    background: var(--nlb-bg-primary);
    border: 1px solid var(--nlb-border-light);
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 32px;
    box-shadow: 0 4px 20px var(--nlb-border-medium);
}

.nodes-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 20px;
}

.nodes-header h4 {
    margin: 0;
    color: var(--nlb-text-primary);
    font-weight: 600;
    flex: 1;
}

.node-count {
    background: var(--nlb-error-light);
    color: var(--nlb-error-dark);
    padding: 4px 12px;
    border-radius: 16px;
    font-size: 0.8rem;
    font-weight: 600;
}

.nodes-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 12px;
}

.node-item {
    display: flex;
    flex-direction: column;
    gap: 12px;
    padding: 16px;
    background: var(--nlb-bg-primary);
    border-radius: 8px;
    border: 1px solid var(--nlb-border-light);
    transition: all 0.2s ease;
    cursor: pointer;
    position: relative;
}

.node-item:hover {
    border-color: var(--nlb-primary);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.node-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
}

.node-name {
    flex: 1;
    font-weight: 500;
}

.node-actions {
    display: flex;
    gap: 4px;
    opacity: 0.8;
    transition: opacity 0.2s ease;
}

.node-item:hover .node-actions {
    opacity: 1;
}

.node-actions .p-button {
    min-width: 40px;
    height: 32px;
    border-radius: 6px;
}

.node-actions .p-button.p-button-text {
    background: rgba(0, 0, 0, 0.05);
    border: 1px solid rgba(0, 0, 0, 0.1);
}

.node-actions .p-button.p-button-text:hover {
    background: rgba(0, 0, 0, 0.1);
    border-color: rgba(0, 0, 0, 0.2);
}

.node-actions .p-button.p-button-danger {
    background: rgba(244, 67, 54, 0.1);
    border: 1px solid rgba(244, 67, 54, 0.3);
    color: #d32f2f;
}

.node-actions .p-button.p-button-danger:hover {
    background: rgba(244, 67, 54, 0.2);
    border-color: rgba(244, 67, 54, 0.5);
}

.terminal-button {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 2px;
}

.terminal-button .arrow-icon {
    font-size: 0.6rem;
    opacity: 0.8;
    margin-left: -2px;
}

.terminal-button:hover .arrow-icon {
    opacity: 1;
    transform: translate(1px, -1px);
    transition: all 0.2s ease;
}

.node-connections {
    display: flex;
    flex-direction: column;
    gap: 8px;
    padding-top: 8px;
    border-top: 1px solid var(--nlb-border-light);
}

.connections-label {
    font-size: 0.8rem;
    color: var(--nlb-text-secondary);
    font-weight: 600;
}

.connection-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.connection-item {
    background: var(--nlb-success-light);
    color: var(--nlb-success-dark);
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 500;
}

.node-indicator {
    color: var(--nlb-success);
    font-size: 0.8rem;
}

/* Routing Tooltip */
.routing-tooltip {
    position: fixed;
    background: white;
    border: 1px solid var(--nlb-border-light);
    border-radius: 8px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    padding: 16px;
    max-width: 500px;
    z-index: 1000;
    font-size: 14px;
}

.tooltip-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--nlb-border-light);
}

.tooltip-header h6 {
    margin: 0;
    color: var(--nlb-text-primary);
    font-size: 16px;
    font-weight: 600;
}

.tooltip-close {
    padding: 4px;
}

.routing-table h6 {
    margin: 0 0 8px 0;
    color: var(--nlb-text-primary);
    font-size: 14px;
    font-weight: 600;
}

.table-container {
    max-height: 200px;
    overflow-y: auto;
    border: 1px solid var(--nlb-border-light);
    border-radius: 4px;
}

.route-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 12px;
}

.route-table th,
.route-table td {
    padding: 6px 8px;
    text-align: left;
    border-bottom: 1px solid var(--nlb-border-light);
}

.route-table th {
    background: var(--nlb-bg-secondary);
    font-weight: 600;
    color: var(--nlb-text-primary);
}

.route-table td {
    color: var(--nlb-text-secondary);
}

/* Deployment Section */
.deployment-info {
    margin-bottom: 32px;
}

.deployment-stats {
    display: flex;
    gap: 24px;
    justify-content: center;
    margin-bottom: 32px;
}

.stat-item {
    display: flex;
    align-items: center;
    gap: 16px;
    background: var(--nlb-bg-primary);
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 2px 10px var(--nlb-border-medium);
    min-width: 200px;
}

.stat-item i {
    font-size: 2rem;
    color: var(--nlb-primary);
}

.stat-number {
    display: block;
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--nlb-text-primary);
}

.stat-label {
    display: block;
    font-size: 0.9rem;
    color: var(--nlb-text-secondary);
    margin-top: 4px;
}

.terminals-section {
    margin-bottom: 32px;
}

.terminals-header {
    text-align: center;
    margin-bottom: 24px;
}

.terminals-header h4 {
    margin: 0 0 8px 0;
    color: var(--nlb-text-primary);
    font-weight: 600;
}

.terminals-header p {
    margin: 0;
    color: var(--nlb-text-secondary);
}

/* Accordion Styling */
.node-accordion {
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 20px var(--nlb-border-medium);
}

.accordion-header {
    display: flex;
    align-items: center;
    gap: 12px;
    width: 100%;
}

.accordion-header span {
    flex: 1;
    font-weight: 600;
}

.node-status {
    padding: 4px 12px;
    border-radius: 16px;
    font-size: 0.8rem;
    font-weight: 600;
}

.node-status.online {
    background: var(--nlb-success-light);
    color: var(--nlb-success-dark);
}

/* Terminal Styling */
.terminal-wrapper {
    padding: 20px 0;
}

.terminal-info {
    margin-bottom: 16px;
    color: var(--nlb-text-secondary);
}

.terminal-iframe {
    width: 100%;
    height: 500px;
    border: 2px solid var(--nlb-border-light);
    border-radius: 8px;
    background: var(--nlb-text-primary);
}

/* Buttons */
.primary-button {
    background: var(--nlb-gradient-primary) !important;
    border: none !important;
    color: var(--nlb-text-light) !important;
    padding: 12px 24px !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
}

.primary-button:hover:not(:disabled) {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px var(--nlb-primary) !important;
}

.action-button {
    width: 100%;
    padding: 12px 16px;
    border-radius: 8px;
    font-weight: 600;
    transition: all 0.3s ease;
}

.action-button.primary {
    background: var(--nlb-bg-primary);
    border: 1.5px solid var(--nlb-border-medium);
    color: var(--nlb-text-primary);
    box-shadow: 0 2px 8px var(--nlb-border-medium);
}

.action-button.primary:hover:not(:disabled) {
    background: var(--nlb-bg-tertiary);
    color: var(--nlb-text-primary);
    box-shadow: 0 4px 16px var(--nlb-border-dark);
}

.action-button.secondary {
    background: var(--nlb-bg-muted);
    border: 1.5px solid var(--nlb-border-light);
    color: var(--nlb-text-secondary);
}

.action-button.secondary:hover {
    background: var(--nlb-bg-primary);
    color: var(--nlb-text-primary);
    border-color: var(--nlb-border-medium);
}

/* Step Actions */
.step-actions {
    display: flex;
    gap: 16px;
    justify-content: center;
    margin-top: 32px;
    padding-top: 24px;
    border-top: 1px solid var(--nlb-border-light);
}



/* Empty State */
.empty-state {
    text-align: center;
    padding: 48px 24px;
    color: var(--nlb-text-secondary);
}

.empty-state i {
    font-size: 3rem;
    margin-bottom: 16px;
    opacity: 0.5;
}

.empty-state h4 {
    margin: 0 0 8px 0;
    color: var(--nlb-text-primary);
}

.empty-state p {
    margin: 0;
}

/* Responsive Design */
@media (max-width: 768px) {
    .lab-controller-container {
        padding: 12px;
    }

    .header-content {
        flex-direction: column;
        gap: 20px;
        text-align: center;
    }

    .progress-steps {
        flex-direction: column;
        gap: 16px;
    }

    .progress-line {
        width: 2px;
        height: 30px;
    }

    .config-grid {
        grid-template-columns: 1fr;
    }

    .deployment-stats {
        flex-direction: column;
        align-items: center;
    }

    .step-actions {
        flex-direction: column;
    }

    .terminal-iframe {
        height: 300px;
    }
}

/* Animation Classes */
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

.step-content {
    animation: fadeInUp 0.5s ease-out;
}

/* Custom Scrollbar */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: var(--nlb-bg-tertiary);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb {
    background: var(--nlb-border-medium);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--nlb-border-dark);
}
</style>
