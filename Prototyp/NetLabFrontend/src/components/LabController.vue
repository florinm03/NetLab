<template>
    <div class="lab-controller-container">
        <!-- Main Header -->
        <div class="header-section">
            <h1 class="page-title">Nodes Controller</h1>
            <p class="page-description">
                Netzwerkknoten effizient verwalten und konfigurieren
            </p>
        </div>
        <!-- <div class="main-header">
            <div class="header-content">
                <div class="header-left">
                    <i class="pi pi-globe header-icon"></i>
                    <div>
                        <h1>Nodes Controller</h1>
                        <p class="header-subtitle">
                            Netzwerkknoten effizient verwalten und konfigurieren
                        </p>
                    </div>
                </div>
            </div>
        </div> -->

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
                                    Wählen Sie die Netzwerktopologie, die Ihren
                                    Testanforderungen am besten entspricht.
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
                                                label="Create Custom Topology"
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
                                                Diese Topologie wird im nächsten
                                                Schritt konfiguriert.
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
                                    Richten Sie Ihre Netzwerkumgebung ein und
                                    starten Sie die Laborsitzung.
                                </p>
                            </div>

                            <div class="config-grid">
                                <!-- Lab Session Card -->
                                <div class="config-card">
                                    <div class="card-header">
                                        <i class="pi pi-play-circle"></i>
                                        <h4>Terminal Session</h4>
                                    </div>
                                    <div class="card-content">
                                        <Button
                                            label="Start TTYD Session"
                                            icon="pi pi-play"
                                            @click="startLab"
                                            :disabled="isLoading"
                                            :loading="isLoading"
                                            class="action-button"
                                        />

                                        <div v-if="error" class="error-message">
                                            <i
                                                class="pi pi-exclamation-triangle"
                                            ></i>
                                            {{ error }}
                                        </div>
                                    </div>
                                </div>

                                <!-- Topology Management Card -->
                                <div class="config-card">
                                    <div class="card-header">
                                        <i class="pi pi-network"></i>
                                        <h4>Topologie Management</h4>
                                    </div>
                                    <div class="card-content">
                                        <Button
                                            label="Topologie erstellen"
                                            icon="pi pi-plus-circle"
                                            @click="createTopology"
                                            class="action-button secondary"
                                        />
                                        <Button
                                            label="Aktive Nodes abfragen"
                                            icon="pi pi-refresh"
                                            @click="getOwnNodes"
                                            class="action-button secondary"
                                        />
                                    </div>
                                </div>
                            </div>

                            <!-- Active Session Info -->
                            <div v-if="container" class="session-info-card">
                                <div class="session-header">
                                    <i class="pi pi-server"></i>
                                    <h4>Aktive Sitzung</h4>
                                    <div
                                        class="status-badge"
                                        :class="
                                            container.details.status.toLowerCase()
                                        "
                                    >
                                        {{ container.details.status }}
                                    </div>
                                </div>

                                <div class="session-details">
                                    <div class="detail-item">
                                        <strong>Container:</strong>
                                        {{ container.container_name }}
                                    </div>
                                </div>

                                <div
                                    v-if="terminalUrl"
                                    class="terminal-section"
                                >
                                    <div class="terminal-header">
                                        <h5>Terminalzugang</h5>
                                        <Button
                                            v-if="!embedTerminal"
                                            label="Open in New Tab"
                                            icon="pi pi-external-link"
                                            @click="openTerminal"
                                            size="small"
                                            text
                                        />
                                    </div>

                                    <div class="terminal-container">
                                        <iframe
                                            :src="String(terminalUrl)"
                                            class="terminal-iframe"
                                            title="Container Terminal"
                                            ref="terminalIframe"
                                            sandbox="allow-same-origin allow-scripts allow-forms allow-popups"
                                            @load="onIframeLoad"
                                            @error="onIframeError"
                                        ></iframe>
                                    </div>

                                    <div
                                        v-if="isConnectingTerminal"
                                        class="connecting-message"
                                    >
                                        <i class="pi pi-spin pi-spinner"></i>
                                        Verbindung zum Terminal wird
                                        hergestellt...
                                    </div>
                                </div>
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
                                        {{ ownNodes.length }} nodes
                                    </div>
                                </div>
                                <div class="nodes-grid">
                                    <div
                                        v-for="(node, index) in ownNodes"
                                        :key="index"
                                        class="node-item"
                                    >
                                        <i
                                            class="pi pi-circle-fill node-indicator"
                                        ></i>
                                        <span>{{
                                            node.name || `Node ${index + 1}`
                                        }}</span>
                                    </div>
                                </div>
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
                                    Greifen Sie auf Ihre bereitgestellten
                                    Netzwerkknoten zu und verwalten Sie sie.
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
                                    <h4>Node Terminals</h4>
                                    <p>
                                        Klicken Sie auf einen beliebigen Knoten,
                                        um auf dessen Terminalschnittstelle
                                        zuzugreifen.
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
                                                    >Node {{ index + 1 }}</span
                                                >
                                                <div class="node-status online">
                                                    Online
                                                </div>
                                            </div>
                                        </template>

                                        <div class="terminal-wrapper">
                                            <div class="terminal-info">
                                                <p>
                                                    Terminal access for Node
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
                                    Bitte gehen Sie zurück und erstellen Sie
                                    Ihre Topologie zuerst.
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

export default {
    created() {
        this.$store.dispatch("initializeUser");
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
    },
    data() {
        return {
            isLoading: false,
            refreshInterval: null,
            error: null,
            container: null,
            terminalUrl: null,
            embedTerminal: true,
            isConnectingTerminal: false,
            connectionAttempts: 0,
            maxConnectionAttempts: 5,
            selectedTopology: null,
            activeStep: "1",
            connectionRetryDelay: 500,
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
            this.container = null;
            this.terminalUrl = null;
            this.error = null;
            this.isLoading = false;
        },
        // startAutoRefresh() {
        //     this.refreshInterval = setInterval(() => {
        //         this.getOwnNodes();
        //     }, 1000);
        // },

        // stopAutoRefresh() {
        //     if (this.refreshInterval) {
        //         clearInterval(this.refreshInterval);
        //         this.refreshInterval = null;
        //     }
        // },

        openTerminal() {
            if (this.terminalUrl) {
                window.open(this.terminalUrl, "_blank");
            }
        },

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

        async startLab() {
            this.isLoading = true;
            this.error = null;
            this.connectionAttempts = 0;

            try {
                const userId = this.userId;

                console.log("User ID:", userId);

                // Start container
                const response = await this.$axios.post("/start-container", {
                    user_id: userId || "guest_user",
                });

                if (response.data.status === "success") {
                    this.container = response.data;

                    // Get terminal URL
                    const ttydResponse = await this.$axios.get(
                        `/ttyd/${this.container.container_name}`,
                    );

                    this.terminalUrl = ttydResponse.data.url;
                    console.log(
                        "Terminal URL:",
                        JSON.stringify(this.terminalUrl),
                    );

                    // Start the connection process
                    this.connectTerminal();
                }
            } catch (error) {
                console.error("Lab start failed:", error);
                this.error = this.getErrorMessage(error);
                this.isLoading = false;
            }
        },

        async connectTerminal() {
            this.isConnectingTerminal = true;
            this.connectionAttempts++;

            try {
                await new Promise((resolve) =>
                    setTimeout(resolve, this.connectionRetryDelay),
                );

                this.$nextTick(() => {
                    if (this.$refs.terminalIframe) {
                        this.$refs.terminalIframe.src = this.terminalUrl;
                    }
                });
            } catch (error) {
                if (this.connectionAttempts < this.maxConnectionAttempts) {
                    console.log(
                        `Connection attempt ${this.connectionAttempts} failed, retrying...`,
                    );
                    setTimeout(() => {
                        this.connectTerminal();
                    }, this.connectionRetryDelay);
                } else {
                    console.error("Max connection attempts reached");
                    this.error =
                        "Failed to connect to terminal after multiple attempts";
                    this.isConnectingTerminal = false;
                    this.isLoading = false;
                }
            }
        },

        onIframeLoad() {
            console.log("Iframe loaded successfully");
            this.isConnectingTerminal = false;
            this.isLoading = false;
        },

        onIframeError() {
            console.error("Iframe failed to load");
            if (this.connectionAttempts < this.maxConnectionAttempts) {
                setTimeout(() => {
                    this.connectTerminal();
                }, this.connectionRetryDelay);
            } else {
                this.error = "Failed to load terminal after multiple attempts";
                this.isConnectingTerminal = false;
                this.isLoading = false;
            }
        },

        getErrorMessage(error) {
            if (error.response) {
                return (
                    error.response.data.message ||
                    `Server error: ${error.response.status}`
                );
            } else if (error.request) {
                return "Network error - is the backend running?";
            } else {
                return "Failed to start lab session";
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
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    height: auto;
}

/* Main Header */
.main-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 16px;
    margin-bottom: 24px;
    box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
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
    background: linear-gradient(45deg, #ffffff, #e0e7ff);
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
    color: #2c3e50;
    margin-bottom: 0.5rem;
}

.page-description {
    font-size: 1.1rem;
    color: #6c757d;
    margin: 0;
}
.user-info {
    display: flex;
    align-items: center;
    gap: 8px;
    background: rgba(255, 255, 255, 0.1);
    padding: 12px 16px;
    border-radius: 12px;
    backdrop-filter: blur(10px);
}

/* Progress Section */
.progress-section {
    background: white;
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 24px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.progress-header h3 {
    margin: 0 0 20px 0;
    color: #2d3748;
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
    background: #e2e8f0;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    transition: all 0.3s ease;
}

.progress-step.active .step-circle {
    background: #667eea;
    color: white;
}

.progress-step.completed .step-circle {
    background: #48bb78;
    color: white;
}

.progress-line {
    width: 60px;
    height: 2px;
    background: #e2e8f0;
    transition: all 0.3s ease;
}

.progress-line.completed {
    background: #48bb78;
}

/* Main Card */
.main-card {
    background: white;
    border-radius: 16px;
    padding: 32px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
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
    color: #2d3748;
    font-size: 1.8rem;
    font-weight: 600;
}

.step-header p {
    margin: 0;
    color: #718096;
    font-size: 1.1rem;
}

.step-icon {
    margin-right: 12px;
    font-size: 1.2rem;
}

/* Topology Selection */
.topology-selection-card {
    background: #f8fafc;
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
    color: #2d3748;
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
    background: #e6fffa;
    border: 1px solid #81e6d9;
    border-radius: 8px;
    padding: 16px;
}

.info-card i {
    color: #319795;
    margin-top: 2px;
}

.info-card strong {
    color: #2d3748;
}

.info-card p {
    margin: 4px 0 0 0;
    color: #4a5568;
}

/* Configuration Grid */
.config-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 24px;
    margin-bottom: 32px;
}

.config-card {
    background: #f8fafc;
    border-radius: 12px;
    padding: 24px;
    border: 1px solid #e2e8f0;
}

.card-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 20px;
    padding-bottom: 16px;
    border-bottom: 1px solid #e2e8f0;
}

.card-header h4 {
    margin: 0;
    color: #2d3748;
    font-weight: 600;
}

.card-content {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

/* Session Info */
.session-info-card {
    background: linear-gradient(135deg, #f0fff4 0%, #f7fafc 100%);
    border: 2px solid #68d391;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 32px;
}

.session-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 20px;
}

.session-header h4 {
    margin: 0;
    color: #2d3748;
    font-weight: 600;
    flex: 1;
}

.status-badge {
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
}

.status-badge.running {
    background: #c6f6d5;
    color: #22543d;
}

.session-details {
    margin-bottom: 20px;
}

.detail-item {
    margin-bottom: 8px;
    color: #4a5568;
}

.terminal-section {
    margin-top: 20px;
}

.terminal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
}

.terminal-header h5 {
    margin: 0;
    color: #2d3748;
    font-weight: 600;
}

.terminal-container {
    border-radius: 8px;
    overflow: hidden;
    border: 2px solid #e2e8f0;
}

/* Nodes Info */
.nodes-info-card {
    background: linear-gradient(135deg, #fffaf0 0%, #f7fafc 100%);
    border: 2px solid #f6ad55;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 32px;
}

.nodes-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 20px;
}

.nodes-header h4 {
    margin: 0;
    color: #2d3748;
    font-weight: 600;
    flex: 1;
}

.node-count {
    background: #fed7d7;
    color: #c53030;
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
    align-items: center;
    gap: 8px;
    padding: 12px;
    background: white;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
}

.node-indicator {
    color: #48bb78;
    font-size: 0.8rem;
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
    background: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    min-width: 200px;
}

.stat-item i {
    font-size: 2rem;
    color: #667eea;
}

.stat-number {
    display: block;
    font-size: 1.5rem;
    font-weight: 700;
    color: #2d3748;
}

.stat-label {
    display: block;
    font-size: 0.9rem;
    color: #718096;
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
    color: #2d3748;
    font-weight: 600;
}

.terminals-header p {
    margin: 0;
    color: #718096;
}

/* Accordion Styling */
.node-accordion {
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
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
    background: #c6f6d5;
    color: #22543d;
}

/* Terminal Styling */
.terminal-wrapper {
    padding: 20px 0;
}

.terminal-info {
    margin-bottom: 16px;
    color: #718096;
}

.terminal-iframe {
    width: 100%;
    height: 500px;
    border: 2px solid #e2e8f0;
    border-radius: 8px;
    background: #1a202c;
}

/* Buttons */
.primary-button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    border: none !important;
    color: white !important;
    padding: 12px 24px !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
}

.primary-button:hover:not(:disabled) {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4) !important;
}

.action-button {
    width: 100%;
    padding: 12px 16px;
    border-radius: 8px;
    font-weight: 600;
    transition: all 0.3s ease;
}

.action-button.secondary {
    background: #f7fafc;
    border: 2px solid #e2e8f0;
    color: #4a5568;
}

.action-button.secondary:hover {
    background: #edf2f7;
    border-color: #cbd5e0;
}

/* Step Actions */
.step-actions {
    display: flex;
    gap: 16px;
    justify-content: center;
    margin-top: 32px;
    padding-top: 24px;
    border-top: 1px solid #e2e8f0;
}

/* Error Messages */
.error-message {
    display: flex;
    align-items: center;
    gap: 8px;
    background: #fed7d7;
    border: 1px solid #feb2b2;
    color: #c53030;
    padding: 12px;
    border-radius: 8px;
    margin-top: 12px;
}

.connecting-message {
    display: flex;
    align-items: center;
    gap: 8px;
    background: #bee3f8;
    border: 1px solid #90cdf4;
    color: #2b6cb0;
    padding: 12px;
    border-radius: 8px;
    margin-top: 12px;
}

/* Empty State */
.empty-state {
    text-align: center;
    padding: 48px 24px;
    color: #718096;
}

.empty-state i {
    font-size: 3rem;
    margin-bottom: 16px;
    opacity: 0.5;
}

.empty-state h4 {
    margin: 0 0 8px 0;
    color: #4a5568;
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
    background: #f1f1f1;
    border-radius: 4px;
}

::-webkit-scrollbar-thumb {
    background: #cbd5e0;
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: #a0aec0;
}
</style>
