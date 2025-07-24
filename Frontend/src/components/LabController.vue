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
                                        <Button
                                            :label="autoRefreshEnabled ? 'Auto-Refresh stoppen' : 'Auto-Refresh starten'"
                                            :icon="autoRefreshEnabled ? 'pi pi-pause' : 'pi pi-play'"
                                            @click="toggleAutoRefresh"
                                            :class="['action-button', autoRefreshEnabled ? 'primary' : 'secondary']"
                                        />
                                        <Button
                                            label="Alle Knoten löschen"
                                            icon="pi pi-trash"
                                            @click="clearAllNodes"
                                            :disabled="ownNodes.length === 0"
                                            class="action-button danger"
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
                                        <div class="status-item">
                                            <span class="status-label">Auto-Refresh:</span>
                                            <span class="status-value" :class="autoRefreshEnabled ? 'status-active' : 'status-inactive'">
                                                {{ autoRefreshEnabled ? 'Aktiv' : 'Inaktiv' }}
                                            </span>
                                        </div>
                                    </div>
                                </div>

                                <!-- PCAP Download Card -->
                                <div class="config-card">
                                    <div class="card-header">
                                        <i class="pi pi-download"></i>
                                        <h4>PCAP Download & Speicherung</h4>
                                    </div>
                                    <div class="card-content">
                                        <p class="pcap-description">
                                            Laden Sie die gemergte PCAP-Datei herunter oder speichern Sie sie in der Datenbank für spätere Analyse.
                                        </p>
                                        <div class="pcap-actions">
                                            <Button
                                                label="PCAP herunterladen"
                                                icon="pi pi-download"
                                                @click="downloadPcap"
                                                :loading="pcapDownloading"
                                                :disabled="ownNodes.length === 0"
                                                class="action-button primary"
                                            />
                                                                                    <Button
                                            label="In Datenbank speichern"
                                            icon="pi pi-database"
                                            @click="savePcapToDatabase"
                                            :loading="pcapSaving"
                                            :disabled="ownNodes.length === 0"
                                            class="action-button secondary"
                                        />
                                        </div>
                                        <div v-if="pcapDownloadStatus" class="pcap-status">
                                            <i :class="pcapDownloadStatus.type === 'success' ? 'pi pi-check-circle' : 'pi pi-exclamation-triangle'"></i>
                                            <span>{{ pcapDownloadStatus.message }}</span>
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
                                        <!-- Node Header -->
                                        <div class="node-header">
                                            <div class="node-info">
                                                <i class="pi pi-circle-fill node-indicator"></i>
                                                <span class="node-name">{{
                                                    getNodeDisplayName(node.name, index)
                                                }}</span>
                                            </div>
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
                                        
                                        <!-- Node Details -->
                                        <div class="node-details">
                                            <div class="node-status-info">
                                                <span class="status-badge" :class="node.status === 'running' ? 'status-running' : 'status-stopped'">
                                                    {{ node.status || 'Online' }}
                                                </span>
                                                <span class="port-info">Port: {{ node.port }}</span>
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
                                                    {{ connection.direction === 'outgoing' ? '→' : '←' }} {{ getNodeName(connection.target) }}
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
                                        <h6>{{ getNodeDisplayName(hoveredNode.name, hoveredNodeIndex) }}</h6>
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
                                    label="Neue Topologie erstellen"
                                    icon="pi pi-plus"
                                    severity="secondary"
                                    @click="createNewTopology"
                                    class="secondary-button"
                                />
                                <Button
                                    label="Zurück"
                                    icon="pi pi-arrow-left"
                                    severity="secondary"
                                    @click="previousStep"
                                />
                                <Button
                                    label="Weiter zu den Terminals"
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
                        Terminals
                    </Step>
                    <StepPanel value="3">
                        <div class="step-content">
                            <div class="step-header">
                                <h3>Terminals</h3>
                                <p>
                                    Hier können Sie auf die Terminals Ihrer aktiven Netzwerkknoten zugreifen, Befehle ausführen und die Netzwerkumgebung direkt steuern.
                                </p>
                            </div>

                            <div class="deployment-info">
                                <div class="deployment-stats">
                                    <div class="stat-item">
                                        <i class="pi pi-server"></i>
                                        <div>
                                            <span class="stat-number">{{
                                                ownNodes.length
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
                                v-if="ownNodes.length > 0"
                                class="terminals-section"
                            >
                                <div class="terminals-header">
                                    <h4>Knoten Terminals</h4>
                                    <p>
                                        Klicken Sie auf einen beliebigen Knoten, um auf dessen Terminalschnittstelle zuzugreifen.
                                    </p>
                                </div>

                                <!-- PCAP Download Section -->
                                <div class="config-card">
                                    <div class="card-header">
                                        <i class="pi pi-download"></i>
                                        <h4>PCAP-Datei herunterladen & speichern</h4>
                                    </div>
                                    <div class="card-content">
                                        <p class="pcap-description">
                                            Laden Sie die gemergte PCAP-Datei herunter oder speichern Sie sie in der Datenbank für spätere Analyse.
                                        </p>
                                        <div class="pcap-actions">
                                            <Button
                                                label="PCAP herunterladen"
                                                icon="pi pi-download"
                                                @click="downloadPcap"
                                                :loading="pcapDownloading"
                                                class="action-button primary"
                                            />
                                                                                    <Button
                                            label="In Datenbank speichern"
                                            icon="pi pi-database"
                                            @click="savePcapToDatabase"
                                            :loading="pcapSaving"
                                            class="action-button secondary"
                                        />
                                        </div>
                                        <div v-if="pcapDownloadStatus" class="pcap-status">
                                            <i :class="pcapDownloadStatus.type === 'success' ? 'pi pi-check-circle' : 'pi pi-exclamation-triangle'"></i>
                                            <span>{{" " + pcapDownloadStatus.message }}</span>
                                        </div>
                                    </div>
                                </div>

                                <Accordion
                                    :multiple="true"
                                    v-model:activeIndex="activeIndexes"
                                    class="node-accordion"
                                >
                                    <AccordionTab
                                        v-for="(node, index) in ownNodes"
                                        :key="index"
                                    >
                                        <template #header>
                                            <div class="accordion-header">
                                                <i class="pi pi-desktop"></i>
                                                <span
                                                    >{{ getNodeDisplayName(node.name, index) }}</span
                                                >
                                                <div class="node-status online">
                                                    {{ node.status || 'Online' }}
                                                </div>
                                            </div>
                                        </template>

                                        <div class="terminal-wrapper">
                                            <div class="terminal-info">
                                                <p>
                                                    Terminalzugang für {{ getNodeDisplayName(node.name, index) }}
                                                </p>
                                            </div>
                                            <iframe
                                                :src="node.url"
                                                class="terminal-iframe"
                                                :title="`Container Terminal ${getNodeDisplayName(node.name, index)}`"
                                                sandbox="allow-same-origin allow-scripts allow-forms allow-popups"
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
        
        <ConfirmDialog />
    </div>
</template>

<script>
import Select from "primevue/select";
import Button from "primevue/button";
import Stepper from "primevue/stepper";
import StepItem from "primevue/stepitem";
import Step from "primevue/step";
import StepPanel from "primevue/steppanel";
import Accordion from "primevue/accordion";
import AccordionTab from "primevue/accordiontab";
import ConfirmDialog from "primevue/confirmdialog";
import { useToast } from "primevue/usetoast";
import { useConfirm } from "primevue/useconfirm";
import TopologyGraph from "./TopologyGraph.vue";

export default {
    async created() {
        this.$store.dispatch("initializeUser");
        await this.checkExistingTopology();
    },
    setup() {
        const toast = useToast();
        const confirm = useConfirm();
        return { toast, confirm };
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
        StepItem,
        StepPanel,
        Accordion,
        AccordionTab,
        ConfirmDialog,
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
            graphNodes: [],
            graphConnections: [],
            hoveredNode: null,
            hoveredNodeIndex: null,
            tooltipPosition: { x: 0, y: 0 },
            refreshInterval: null,
            autoRefreshEnabled: false,
            pcapDownloading: false,
            pcapSaving: false,
            pcapDownloadStatus: null,
        };
    },
    watch: {
        activeStep(newVal) {
            if (parseInt(newVal) === 2) {
                this.getOwnNodes();
                this.startAutoRefresh();
            } else {
                this.stopAutoRefresh();
            }
        },
    },
    beforeUnmount() {
        this.stopAutoRefresh();
    },
    methods: {
        async nextStep() {
            console.log("selectedTopology", this.selectedTopology);
            const currentStep = parseInt(this.activeStep);
            if (currentStep < 3) {
                this.activeStep = String(currentStep + 1);

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
            if (this.ownNodes.length > 0) {
                this.confirm.require({
                    message: 'Möchten Sie wirklich alle Ihre bestehenden Knoten löschen und den Prozess neu starten?',
                    header: 'Prozess Neustarten',
                    icon: 'pi pi-exclamation-triangle',
                    acceptClass: 'p-button-danger',
                    acceptLabel: 'Ja',
                    rejectLabel: 'Nein',
                    accept: () => {
                        this.clearTopologyAndRestart();
                    },
                    reject: () => {
                        this.toast.add({
                            severity: 'info',
                            summary: 'Abgebrochen',
                            detail: 'Prozess wurde nicht neu gestartet.',
                            life: 3000
                        });
                    }
                });
            } else {
                this.clearTopologyAndRestart();
            }
        },

        async clearTopologyAndRestart() {
            try {
                const userId = this.userId;
                const response = await this.$axios.delete(`/clear-topology/${userId}`);
                
                if (response.data.status === 'success') {
                    this.activeStep = "1";
                    this.selectedTopology = null;
                    this.isLoading = false;
                    this.ownNodes = [];
                    this.graphNodes = [];
                    this.graphConnections = [];
                    this.stopAutoRefresh();
                    
                    this.toast.add({
                        severity: 'success',
                        summary: 'Prozess Neustart',
                        detail: 'Alle Knoten wurden erfolgreich entfernt und der Prozess neu gestartet.',
                        life: 3000
                    });
                } else {
                    this.toast.add({
                        severity: 'error',
                        summary: 'Fehler',
                        detail: 'Knoten konnten nicht gelöscht werden.',
                        life: 3000
                    });
                }
            } catch (error) {
                console.error('Error clearing topology:', error);
                this.toast.add({
                    severity: 'error',
                    summary: 'Fehler',
                    detail: 'Topologie konnte nicht gelöscht werden.',
                    life: 3000
                });
            }
        },

        createNewTopology() {
            if (this.ownNodes.length > 0) {
                this.confirm.require({
                    message: 'Möchten Sie wirklich alle Ihre bestehenden Knoten löschen und eine neue Topologie erstellen?',
                    header: 'Neue Topologie erstellen',
                    icon: 'pi pi-exclamation-triangle',
                    acceptClass: 'p-button-danger',
                    acceptLabel: 'Ja',
                    rejectLabel: 'Nein',
                    accept: () => {
                        this.clearTopologyAndReset();
                    },
                    reject: () => {
                        this.toast.add({
                            severity: 'info',
                            summary: 'Abgebrochen',
                            detail: 'Neue Topologie wurde nicht erstellt.',
                            life: 3000
                        });
                    }
                });
            } else {
                this.clearTopologyAndReset();
            }
        },

        async clearTopologyAndReset() {
            try {
                const userId = this.userId;
                const response = await this.$axios.delete(`/clear-topology/${userId}`);
                
                if (response.data.status === 'success') {
                    this.ownNodes = [];
                    this.graphNodes = [];
                    this.graphConnections = [];
                    this.selectedTopology = null;
                    this.activeStep = "1";
                    this.stopAutoRefresh();
                    
                    this.toast.add({
                        severity: 'success',
                        summary: 'Topologie gelöscht',
                        detail: 'Alle Knoten wurden erfolgreich entfernt. Sie können jetzt eine neue Topologie erstellen.',
                        life: 3000
                    });
                } else {
                    this.toast.add({
                        severity: 'error',
                        summary: 'Fehler',
                        detail: 'Knoten konnten nicht gelöscht werden.',
                        life: 3000
                    });
                }
            } catch (error) {
                console.error('Error clearing topology:', error);
                this.toast.add({
                    severity: 'error',
                    summary: 'Fehler',
                    detail: 'Topologie konnte nicht gelöscht werden.',
                    life: 3000
                });
            }
        },

        startAutoRefresh() {
            if (this.refreshInterval) {
                this.stopAutoRefresh();
            }
            
            this.autoRefreshEnabled = true;
            this.refreshInterval = setInterval(async () => {
                if (this.autoRefreshEnabled) {
                    await this.getOwnNodes();
                }
            }, 3000);
            
            console.log('Auto-refresh started');
        },

        stopAutoRefresh() {
            if (this.refreshInterval) {
                clearInterval(this.refreshInterval);
                this.refreshInterval = null;
            }
            this.autoRefreshEnabled = false;
            console.log('Auto-refresh stopped');
        },

        toggleAutoRefresh() {
            if (this.autoRefreshEnabled) {
                this.stopAutoRefresh();
                this.toast.add({
                    severity: 'info',
                    summary: 'Auto-Refresh',
                    detail: 'Automatische Aktualisierung gestoppt',
                    life: 2000
                });
            } else {
                this.startAutoRefresh();
                this.toast.add({
                    severity: 'success',
                    summary: 'Auto-Refresh',
                    detail: 'Automatische Aktualisierung gestartet',
                    life: 2000
                });
            }
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
                    console.error(
                        response.data.message || "Failed to create topology",
                    );
                }
            } catch (err) {
            } finally {
            }
        },

        async checkExistingTopology() {
            try {
                const userId = this.userId;
                
                const terminal_urls_response = await this.$axios.get(
                    "/ttyd/getOwnNodes",
                    {
                        params: { user_id: userId },
                    },
                );

                if (terminal_urls_response.data.status === "success") {
                    const terminals = terminal_urls_response.data.terminals;
                    
                    this.ownNodes = terminals
                        .filter(terminal => !terminal.container_name.includes('pcap-merger')) // Exclude pcap-merger
                        .map((terminal, index) => ({
                            name: terminal.container_name,
                            id: terminal.container_name,
                            ip: `172.16.0.${index + 1}`,
                            port: terminal.port,
                            status: terminal.status,
                            url: terminal.url
                        }));
                    
                    if (this.ownNodes.length > 0) {
                        this.activeStep = "2";
                        this.selectedTopology = this.determineTopologyType();
                        this.updateGraphData();
                        
                        this.toast.add({
                            severity: 'info',
                            summary: 'Bestehende Topologie gefunden',
                            detail: `Sie haben bereits ${this.ownNodes.length} aktive Knoten. Sie können direkt mit der Konfiguration fortfahren.`,
                            life: 5000
                        });
                    }
                    
                    console.log("Terminal data:", JSON.stringify(terminal_urls_response.data));
                    console.log("Processed nodes:", JSON.stringify(this.ownNodes));
                } else {
                    console.log(
                        "error getting terminals :",
                        JSON.stringify(terminal_urls_response),
                    );
                }
            } catch (err) {
                console.error("Error fetching terminals:", err);
            }
        },

        async getOwnNodes() {
            try {
                this.isLoading = true;
                const userId = this.userId;

                const terminal_urls_response = await this.$axios.get(
                    "/ttyd/getOwnNodes",
                    {
                        params: { user_id: userId },
                    },
                );

                if (terminal_urls_response.data.status === "success") {
                    const terminals = terminal_urls_response.data.terminals;
                    
                    this.ownNodes = terminals
                        .filter(terminal => !terminal.container_name.includes('pcap-merger'))
                        .map((terminal, index) => ({
                            name: terminal.container_name,
                            id: terminal.container_name,
                            ip: `172.16.0.${index + 1}`,
                            port: terminal.port,
                            status: terminal.status,
                            url: terminal.url
                        }));
                    
                    this.updateGraphData();
                    console.log("Terminal data:", JSON.stringify(terminal_urls_response.data));
                    console.log("Processed nodes:", JSON.stringify(this.ownNodes));
                } else {
                    console.log(
                        "error getting terminals :",
                        JSON.stringify(terminal_urls_response),
                    );
                }
            } catch (err) {
                console.error("Error fetching terminals:", err);
            } finally {
                this.isLoading = false;
            }
        },

        updateGraphData() {
            this.graphNodes = this.ownNodes.map((node, index) => ({
                id: node.name || `node-${index}`,
                name: node.name || `Knoten ${index + 1}`,
                ip: node.ip || `172.16.0.${index + 1}`,
                status: 'online',
                type: 'router'
            }));

            this.graphConnections = this.generateConnections();
        },

        generateConnections() {
            const connections = [];
            const nodeCount = this.graphNodes.length;
            
            console.log('Generating connections for topology:', this.selectedTopology?.code);
            console.log('Nodes:', this.graphNodes.map(n => ({ id: n.id, name: n.name })));

            if (this.selectedTopology?.code === 'ring') {
                for (let i = 0; i < nodeCount; i++) {
                    const next = (i + 1) % nodeCount;
                    connections.push({
                        source: this.graphNodes[i].id,
                        target: this.graphNodes[next].id,
                        type: 'ethernet'
                    });
                }
            } else if (this.selectedTopology?.code === 'mesh') {    
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
                for (let i = 0; i < nodeCount - 1; i++) {
                    connections.push({
                        source: this.graphNodes[i].id,
                        target: this.graphNodes[i + 1].id,
                        type: 'ethernet'
                    });
                }
            }
            
            console.log('Generated connections:', connections);
            return connections;
        },

        onNodeClick(node) {
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
                console.log('Fetching routing table for node:', node.name);
                const response = await this.$axios.get(`/node-routing/${node.name}`);
                console.log('Routing table response:', response.data);
                
                if (response.data.status === 'success') {
                    const realRoutes = response.data.routes;
                    
                    if (realRoutes && realRoutes.length > 0) {
                        console.log('Successfully fetched routes:', realRoutes);
                        return realRoutes;
                    } else {
                        throw new Error('Keine Routing-Daten verfügbar');
                    }
                } else {
                    throw new Error(response.data.message || 'Fehler beim Abrufen der Routing-Tabelle');
                }
            } catch (error) {
                console.error('Error fetching routing table:', error);
                console.error('Node data:', node);
                const nodeIndex = this.ownNodes.findIndex(n => n.name === node.name);
                const nodeNumber = this.getNodeDisplayName(node.name, nodeIndex);
                return [
                    {
                        destination: `Node ${nodeNumber} (Fehler)`,
                        gateway: 'N/A',
                        genmask: 'N/A',
                        flags: 'N/A',
                        iface: 'N/A'
                    },
                    {
                        destination: 'Fehler beim Abrufen der Routing-Tabelle',
                        gateway: error.message || 'Unbekannter Fehler',
                        genmask: 'N/A',
                        flags: 'N/A',
                        iface: 'N/A'
                    }
                ];
            }
        },

        getNodeConnections(node, index) {
            // console.log(`Getting connections for node: ${node.name} (index: ${index})`);
            // console.log('All graph connections:', this.graphConnections);
            
            const connections = this.graphConnections.filter(conn => {
                const isSource = conn.source === node.name;
                const isTarget = conn.target === node.name;
                
                // console.log(`Connection ${conn.source} -> ${conn.target}: isSource=${isSource}, isTarget=${isTarget}`);
                
                return isSource || isTarget;
            });
            
            // console.log('Filtered connections for node:', connections);
            
            const result = connections.map(conn => {
                const isSource = conn.source === node.name;
                return {
                    ...conn,
                    direction: isSource ? 'outgoing' : 'incoming',
                    target: isSource ? conn.target : conn.source
                };
            });
            
            // console.log('Final connections for node:', result);
            return result;
        },

        getNodeName(nodeId) {
            const node = this.ownNodes.find(n => n.name === nodeId);
            if (node) {
                return this.getNodeDisplayName(node.name, this.ownNodes.indexOf(node));
            }
            return nodeId;
        },

        async deleteNode(node) {
            try {
                const userId = this.userId;
                const response = await this.$axios.delete(`/delete-node/${userId}/${node.id}`);
                
                if (response.data.status === 'success') {
                    this.ownNodes = this.ownNodes.filter(n => n.name !== node.name);
                    this.updateGraphData();
                    
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
            if (node.url) {
                // console.log(`Opening terminal for node: ${node.name}`, node.url);
                window.open(node.url, '_blank');
            } else {
                console.error(`No terminal URL found for node: ${node.name}`);
                console.log('Node data:', node);
                
                this.toast.add({
                    severity: 'error',
                    summary: 'Terminal nicht verfügbar',
                    detail: `Terminal für Knoten "${node.name}" konnte nicht gefunden werden`,
                    life: 3000
                });
            }
        },

        async clearAllNodes() {
            this.confirm.require({
                message: 'Möchten Sie wirklich alle Ihre bestehenden Knoten löschen?',
                header: 'Alle Knoten löschen',
                icon: 'pi pi-exclamation-triangle',
                acceptClass: 'p-button-danger',
                acceptLabel: 'Ja',
                rejectLabel: 'Nein',
                accept: async () => {
                    try {
                        const userId = this.userId;
                        const response = await this.$axios.delete(`/clear-topology/${userId}`);
                        
                        if (response.data.status === 'success') {
                            this.ownNodes = [];
                            this.graphNodes = [];
                            this.graphConnections = [];
                            
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
                reject: () => {
                    this.toast.add({
                        severity: 'info',
                        summary: 'Abgebrochen',
                        detail: 'Knoten wurden nicht gelöscht.',
                        life: 3000
                    });
                }
            });
        },

        onIframeError(event) {
            console.error('Iframe failed to load:', event);
            this.toast.add({
                severity: 'error',
                summary: 'Terminal Fehler',
                detail: 'Terminal konnte nicht geladen werden',
                life: 3000
            });
        },

        determineTopologyType() {
            // this.selectedTopology
            const nodeCount = this.ownNodes.length;
            
            console.log('Determining topology type for', nodeCount, 'nodes');
            
            let topology;
            if (nodeCount === 2) {
                topology = { name: "Mini-Ring", code: "mini_ring" };
            } else if (nodeCount === 3) {
                topology = { name: "Ring", code: "ring" };
            } else if (nodeCount === 4) {
                topology = { name: "Mesh", code: "mesh" };
            } else if (nodeCount === 5) {
                topology = { name: "Star", code: "star" };
            } else if (nodeCount >= 6) {
                topology = { name: "Tree", code: "tree" };
            } else {
                topology = { name: "Star", code: "star" };
            }
            
            console.log('Determined topology:', topology);
            return topology;
        },

        getNodeDisplayName(containerName, index) {
            if (!containerName) {
                return `${index + 1}`;
            }
            
            const match = containerName.match(/_(\d+)$/);
            if (match) {
                return match[1];
            }
            
            const numberMatch = containerName.match(/(\d+)/);
            if (numberMatch) {
                return numberMatch[1];
            }
            
            return `${index + 1}`;
        },

        async downloadPcap() {
            try {
                this.pcapDownloading = true;
                this.pcapDownloadStatus = null;
                
                const userId = this.userId;
                // console.log("--------------------------------");
                // console.log('Downloading PCAP for user:', userId);
                const response = await this.$axios.get(`/download-pcap/${userId}`, {
                    responseType: 'blob'
                });
                
                // Create a download link with timestamp
                const blob = new Blob([response.data], { 
                    type: 'application/vnd.tcpdump.pcap' 
                });
                const url = window.URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = url;
                
                // Add timestamp and topology type to filename
                const now = new Date();
                const timestamp = now.toISOString()
                    .replace(/[:.]/g, '-')  // Replace colons and dots with hyphens
                    .replace('T', '_')      // Replace T with underscore
                    .slice(0, 16);          // Remove seconds, milliseconds and timezone
                
                // Get topology type from selected topology
                const topologyType = this.selectedTopology ? this.selectedTopology.code : 'unknown';
                
                link.download = `merged_pcap_${userId}_${topologyType}_${timestamp}.pcap`;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                window.URL.revokeObjectURL(url);
                
                this.pcapDownloadStatus = {
                    type: 'success',
                    message: 'PCAP-Datei erfolgreich heruntergeladen'
                };
                
                this.toast.add({
                    severity: 'success',
                    summary: 'PCAP Download',
                    detail: 'PCAP-Datei wurde erfolgreich heruntergeladen',
                    life: 3000
                });
                
            } catch (error) {
                console.error('Error downloading PCAP:', error);
                
                let errorMessage = 'Fehler beim Herunterladen der PCAP-Datei';
                
                if (error.response) {
                    if (error.response.status === 404) {
                        errorMessage = 'PCAP-Datei nicht gefunden. Stellen Sie sicher, dass Ihre Topologie aktiv ist.';
                    } else if (error.response.status === 500) {
                        errorMessage = 'Server-Fehler beim Herunterladen der PCAP-Datei';
                    }
                }
                
                this.pcapDownloadStatus = {
                    type: 'error',
                    message: errorMessage
                };
                
                this.toast.add({
                    severity: 'error',
                    summary: 'PCAP Download Fehler',
                    detail: errorMessage,
                    life: 5000
                });
            } finally {
                this.pcapDownloading = false;
            }
        },

        async savePcapToDatabase() {
            try {
                this.pcapSaving = true;
                this.pcapDownloadStatus = null;
                
                const userId = this.userId;
                // console.log("--------------------------------");
                // console.log('Saving PCAP to database for user:', userId);
                
                // Prepare topology info
                const topologyInfo = {
                    name: this.selectedTopology ? this.selectedTopology.name : 'Unknown',
                    type: this.selectedTopology ? this.selectedTopology.code : 'unknown',
                    node_count: this.ownNodes.length,
                    capture_duration: 0 // Could be calculated if we track start time
                };
                
                // Prepare connections info
                const connections = this.graphConnections.map(conn => ({
                    source: conn.source,
                    target: conn.target,
                    type: 'ethernet'
                }));
                
                const response = await this.$axios.post(`/save-pcap/${userId}`, {
                    topology_info: topologyInfo,
                    connections: connections
                });
                
                if (response.data.status === 'success') {
                    this.pcapDownloadStatus = {
                        type: 'success',
                        message: `PCAP-Datei erfolgreich in Datenbank gespeichert (ID: ${response.data.pcap_id})`
                    };
                    
                    this.toast.add({
                        severity: 'success',
                        summary: 'PCAP Speicherung',
                        detail: 'PCAP-Datei wurde erfolgreich in der Datenbank gespeichert',
                        life: 5000
                    });
                } else {
                    throw new Error(response.data.message || 'Unknown error');
                }
                
            } catch (error) {
                console.error('Error saving PCAP to database:', error);
                
                let errorMessage = 'Fehler beim Speichern der PCAP-Datei in der Datenbank';
                
                if (error.response) {
                    if (error.response.status === 404) {
                        errorMessage = 'PCAP-Datei nicht gefunden. Stellen Sie sicher, dass Ihre Topologie aktiv ist.';
                    } else if (error.response.status === 500) {
                        errorMessage = 'Server-Fehler beim Speichern der PCAP-Datei';
                    } else if (error.response.data && error.response.data.message) {
                        errorMessage = error.response.data.message;
                    }
                }
                
                this.pcapDownloadStatus = {
                    type: 'error',
                    message: errorMessage
                };
                
                this.toast.add({
                    severity: 'error',
                    summary: 'PCAP Speicherung Fehler',
                    detail: errorMessage,
                    life: 5000
                });
            } finally {
                this.pcapSaving = false;
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

.node-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    margin-bottom: 8px;
}

.node-info {
    display: flex;
    align-items: center;
    gap: 8px;
    flex: 1;
    min-width: 0; /* Allow text to truncate */
}

.node-name {
    font-weight: 600;
    color: var(--nlb-text-primary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.node-actions {
    display: flex;
    gap: 4px;
    opacity: 0.7;
    transition: opacity 0.2s ease;
    flex-shrink: 0; /* Prevent buttons from shrinking */
}

.node-item:hover .node-actions {
    opacity: 1;
}

.node-details {
    display: flex;
    flex-direction: column;
    gap: 8px;
    padding: 8px 0;
}

.node-status-info {
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
}

.status-badge {
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
}

.status-badge.status-running {
    background: var(--nlb-success-light);
    color: var(--nlb-success-dark);
}

.status-badge.status-stopped {
    background: var(--nlb-error-light);
    color: var(--nlb-error-dark);
}

.port-info {
    font-size: 0.8rem;
    color: var(--nlb-text-secondary);
    font-weight: 500;
}

.node-actions .p-button {
    min-width: 40px;
    height: 32px;
    border-radius: 6px;
}

.node-actions .p-button.p-button-text {
    background: var(--nlb-bg-secondary);
    border: 1px solid var(--nlb-border-light);
    color: var(--nlb-text-secondary);
    transition: all 0.2s ease;
}

.node-actions .p-button.p-button-text:hover {
    background: var(--nlb-primary);
    border-color: var(--nlb-primary);
    color: var(--nlb-text-light);
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.node-actions .p-button.p-button-danger {
    background: var(--nlb-error-light);
    border: 1px solid var(--nlb-error);
    color: var(--nlb-error-dark);
    transition: all 0.2s ease;
}

.node-actions .p-button.p-button-danger:hover {
    background: var(--nlb-error);
    border-color: var(--nlb-error-dark);
    color: var(--nlb-text-light);
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(244, 67, 54, 0.3);
}

.terminal-button {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 2px;
    position: relative;
}

.terminal-button .arrow-icon {
    font-size: 0.6rem;
    opacity: 0.8;
    margin-left: -2px;
    transition: all 0.2s ease;
}

.terminal-button:hover .arrow-icon {
    opacity: 1;
    transform: translate(1px, -1px);
}

.node-connections {
    display: flex;
    flex-direction: column;
    gap: 8px;
    padding-top: 12px;
    border-top: 1px solid var(--nlb-border-light);
    margin-top: 8px;
}

.connections-label {
    font-size: 0.8rem;
    color: var(--nlb-text-secondary);
    font-weight: 600;
    margin-bottom: 4px;
}

.connection-list {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
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

.secondary-button {
    background: var(--nlb-bg-secondary) !important;
    border: 1.5px solid var(--nlb-border-medium) !important;
    color: var(--nlb-text-primary) !important;
    padding: 12px 24px !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
}

.secondary-button:hover:not(:disabled) {
    background: var(--nlb-bg-tertiary) !important;
    border-color: var(--nlb-border-dark) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px var(--nlb-border-medium) !important;
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

.action-button.danger {
    background: var(--nlb-bg-primary);
    border: 1.5px solid var(--nlb-border-medium);
    color: var(--nlb-text-primary);
    box-shadow: 0 2px 8px var(--nlb-border-medium);
}

.action-button.danger:hover:not(:disabled) {
    background: var(--nlb-error);
    color: var(--nlb-text-light);
    box-shadow: 0 4px 16px var(--nlb-error);
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

/* PCAP Download Styling */
.pcap-description {
    color: var(--nlb-text-secondary);
    margin-bottom: 16px;
    font-size: 0.9rem;
    line-height: 1.4;
}

.pcap-actions {
    display: flex;
    gap: 12px;
    margin-bottom: 16px;
    flex-wrap: wrap;
}

.pcap-actions .action-button {
    flex: 1;
    min-width: 150px;
}

.pcap-status {
    margin-top: 12px;
    padding: 8px 12px;
    border-radius: 6px;
    font-size: 0.9rem;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 8px;
}

.pcap-status i {
    font-size: 1rem;
}

.pcap-status .success {
    color: var(--nlb-success-dark);
}

.pcap-status .error {
    color: var(--nlb-error-dark);
}

.config-card:has(.pcap-description) {
    background: var(--nlb-bg-primary);
    border-radius: 12px;
    padding: 24px;
    border: 1px solid var(--nlb-border-light);
    transition: all 0.3s ease;
    box-shadow: 0 4px 20px var(--nlb-border-medium);
}
</style>
