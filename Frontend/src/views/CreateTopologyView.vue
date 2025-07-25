<template>
    <div class="topology-creator">
        <!-- Modern Header Section -->
        <div class="header-section">
            <div class="header-content">
                <div class="header-text">
                    <h1 class="main-title">Topologie erstellen</h1>
                    <p class="subtitle">
                        Wählen Sie ein Beispiel aus oder schreiben Sie Ihre eigene Topologie
                    </p>
                </div>
                <div class="header-stats">
                    <div class="stat-card">
                        <div class="stat-number">{{ topologyExamples.length }}</div>
                        <div class="stat-label">Beispiele</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{{ topologyTypes.length }}</div>
                        <div class="stat-label">Topologie-Typen</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{{ editorContent.length > 0 ? 'Aktiv' : 'Leer' }}</div>
                        <div class="stat-label">Editor Status</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Main Content Section -->
        <div class="content-section">
            <!-- Carousel Section -->
            <div class="carousel-section">
                <div class="section-header">
                    <h2 class="section-title">Beispiel-Topologien</h2>
                    <p class="section-description">
                        Wählen Sie eine Vorlage als Ausgangspunkt für Ihre Topologie
                    </p>
                </div>
                <Carousel
                    :value="topologyExamples"
                    :numVisible="3"
                    :numScroll="1"
                    :responsiveOptions="responsiveOptions"
                    class="topology-carousel"
                >
                    <template #item="{ data }">
                        <div class="example-card" @click="selectExample(data)">
                            <div class="card-header">
                                <h4>{{ data.name }}</h4>
                                <span class="card-badge">{{ data.type }}</span>
                            </div>
                            <p class="card-description">{{ data.description }}</p>
                            <div class="card-preview">
                                <pre><code>{{ data.preview }}</code></pre>
                            </div>
                            <Button
                                label="Verwenden"
                                icon="pi pi-check"
                                class="p-button-sm p-button-outlined"
                                @click.stop="selectExample(data)"
                            />
                        </div>
                    </template>
                </Carousel>
            </div>

            <!-- Editor Section -->
            <div class="editor-section">
                <div class="section-header">
                    <h2 class="section-title">Python Code Editor</h2>
                    <div class="editor-actions">
                        <Button
                            label="Beispiel löschen"
                            icon="pi pi-trash"
                            class="p-button-secondary p-button-outlined p-button-sm"
                            @click="clearEditor"
                        />
                        <Button
                            label="Validieren"
                            icon="pi pi-check-circle"
                            class="p-button-info p-button-sm"
                            @click="validateCode"
                            :loading="validating"
                        />
                    </div>
                </div>

                <Editor
                    v-model="editorContent"
                    editorStyle="height: 400px"
                    placeholder="Schreiben Sie hier Ihren Python-Code für die Topologie..."
                    class="topology-editor"
                >
                </Editor>
            </div>

            <!-- Metadata Section -->
            <div class="metadata-section">
                <div class="section-header">
                    <h2 class="section-title">Topologie Informationen</h2>
                    <p class="section-description">
                        Geben Sie die grundlegenden Informationen für Ihre Topologie ein
                    </p>
                </div>
                <div class="metadata-form">
                    <div class="form-row">
                        <div class="form-group">
                            <label for="topology-name">Name</label>
                            <InputText
                                id="topology-name"
                                v-model="topologyName"
                                placeholder="Geben Sie einen Namen für die Topologie ein"
                                class="w-full"
                            />
                        </div>
                        <div class="form-group">
                            <label for="topology-type">Typ</label>
                            <Dropdown
                                id="topology-type"
                                v-model="topologyType"
                                :options="topologyTypes"
                                optionLabel="label"
                                optionValue="value"
                                placeholder="Wählen Sie einen Typ"
                                class="w-full"
                            />
                        </div>
                    </div>
                    <div class="form-group">
                        <label for="topology-description">Beschreibung</label>
                        <Textarea
                            id="topology-description"
                            v-model="topologyDescription"
                            rows="3"
                            placeholder="Beschreiben Sie die Topologie..."
                            class="w-full"
                        />
                    </div>
                </div>
            </div>

            <!-- Action Buttons -->
            <div class="action-section">
                <Button
                    label="Abbrechen"
                    icon="pi pi-times"
                    class="p-button-secondary"
                    @click="resetForm"
                />
                <Button
                    label="Topologie erstellen"
                    icon="pi pi-send"
                    class="p-button-primary"
                    @click="submitTopology"
                    :loading="submitting"
                    :disabled="!canSubmit"
                />
            </div>
        </div>

        <!-- Toast for notifications -->
        <Toast />
    </div>
</template>

<script>
import { ref, computed, inject } from "vue";
import Carousel from "primevue/carousel";
import Editor from "primevue/editor";
import Button from "primevue/button";
import InputText from "primevue/inputtext";
import Dropdown from "primevue/dropdown";
import Textarea from "primevue/textarea";
import Toast from "primevue/toast";
import { useToast } from "primevue/usetoast";

export default {
    name: "TopologyCreator",
    components: {
        Carousel,
        Editor,
        Button,
        InputText,
        Dropdown,
        Textarea,
        Toast,
    },
    setup() {
        const apiClient = inject("axios");
        const toast = useToast();

        // Form data
        const editorContent = ref("");
        const topologyName = ref("");
        const topologyType = ref("");
        const topologyDescription = ref("");
        const submitting = ref(false);
        const validating = ref(false);

        // Topology types
        const topologyTypes = [
            { label: "Ring Topologie", value: "ring" },
            { label: "Star Topologie", value: "star" },
            { label: "Mesh Topologie", value: "mesh" },
            { label: "Bus Topologie", value: "bus" },
            { label: "Tree Topologie", value: "tree" },
            { label: "Hybrid Topologie", value: "hybrid" },
        ];

        // TODO: topologies
        const topologyExamples = ref([
            {
                id: 1,
                name: "Ring Topologie",
                type: "Ring",
                description: "Eine einfache Ring-Topologie mit mehreren Knoten",
                preview:
                    'from net_lab_builder.network_controller import NetworkController\n\nnc = NetworkController()\nn1 = nc.create_node(base_name="node")',
                code: `from net_lab_builder.network_controller import NetworkController

nc = None
try:
    nc = NetworkController()

    # Knoten erstellen
    n1 = nc.create_node(base_name="node")
    n2 = nc.create_node(base_name="node")
    n3 = nc.create_node(base_name="node")

    # Netzwerke erstellen
    net1 = nc.create_network()
    net2 = nc.create_network()
    net3 = nc.create_network()

    # Ring-Verbindungen
    nc.connect_node_to_network(net1, n1, n2)
    nc.connect_node_to_network(net2, n2, n3)
    nc.connect_node_to_network(net3, n3, n1)

    # Topologie starten
    for node in [n1, n2, n3]:
        node.start_tcpdump()

    print("Running... Press Ctrl+C to stop.")

    nc.pcap_merge()
except KeyboardInterrupt:
    pass
finally:
    if nc:
        nc.stop_all_nodes()
        nc.prune_all()

if __name__ == "__main__":
    mini_ring_topology()`,
            },
            {
                id: 2,
                name: "Star Topologie",
                type: "Star",
                description: "Zentrale Star-Topologie mit einem Hub",
                preview:
                    'hub = nc.create_node(base_name="hub")\nfor i in range(4):\n    node = nc.create_node()',
                code: `from net_lab_builder.network_controller import NetworkController

nc = None
try:
    nc = NetworkController()

    # Hub erstellen
    hub = nc.create_node(base_name="hub")

    # Client-Knoten erstellen
    clients = []
    for i in range(4):
        client = nc.create_node(base_name=f"client")
        clients.append(client)

    # Zentrales Netzwerk
    central_net = nc.create_network()

    # Alle Clients mit Hub verbinden
    for client in clients:
        nc.connect_node_to_network(central_net, hub, client)

    # Alle Knoten starten
    all_nodes = [hub] + clients
    for node in all_nodes:
        node.start_tcpdump()

    print("Star topology running... Press Ctrl+C to stop.")

    nc.pcap_merge()
except KeyboardInterrupt:
    pass
finally:
    if nc:
        nc.stop_all_nodes()
        nc.prune_all()

if __name__ == "__main__":
    star_topology()`,
            },
            {
                id: 3,
                name: "Mesh Topologie",
                type: "Mesh",
                description: "Vollständig vermaschte Topologie",
                preview:
                    "nodes = []\nfor i in range(4):\n    nodes.append(nc.create_node())",
                code: `from net_lab_builder.network_controller import NetworkController

nc = None
try:
    nc = NetworkController()

    # Knoten erstellen
    nodes = []
    for i in range(4):
        node = nc.create_node(base_name="mesh_node")
        nodes.append(node)

    # Vollständige Vermaschung - jeder mit jedem
    networks = []
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            network = nc.create_network()
            nc.connect_node_to_network(network, nodes[i], nodes[j])
            networks.append(network)

    # Alle Knoten starten
    for node in nodes:
        node.start_tcpdump()

    print(f"Mesh topology with {len(nodes)} nodes running...")
    print("Press Ctrl+C to stop.")

    nc.pcap_merge()
except KeyboardInterrupt:
    pass
finally:
    if nc:
        nc.stop_all_nodes()
        nc.prune_all()

if __name__ == "__main__":
    mesh_topology()`,
            },
        ]);

        const responsiveOptions = [ 
            {
                breakpoint: "1024px",
                numVisible: 2,
                numScroll: 1,
            },
            {
                breakpoint: "768px",
                numVisible: 1,
                numScroll: 1,
            },
        ];

        const canSubmit = computed(() => {
            return (
                topologyName.value.trim() &&
                topologyType.value &&
                editorContent.value.trim() &&
                !submitting.value
            );
        });

        const selectExample = (example) => {
            editorContent.value = example.code;
            topologyName.value = example.name;
            topologyType.value = example.type.toLowerCase();
            topologyDescription.value = example.description;

            toast.add({
                severity: "success",
                summary: "Beispiel geladen",
                detail: `${example.name} wurde in den Editor geladen`,
                life: 3000,
            });
        };

        const clearEditor = () => {
            editorContent.value = "";
            toast.add({
                severity: "info",
                summary: "Editor geleert",
                detail: "Der Editor-Inhalt wurde gelöscht",
                life: 3000,
            });
        };

        const validateCode = async () => {
            console.log("Validating code...");

            if (!editorContent.value.trim()) {
                toast.add({
                    severity: "warn",
                    summary: "Kein Code",
                    detail: "Bitte geben Sie Python-Code ein",
                    life: 3000,
                });
                return;
            }

            validating.value = true;
            try {
                const textWithoutTags = editorContent.value
                    .replace(/<[^>]*>/g, "")
                    .trim();

                const response = await apiClient.post("validate-python", {
                    code: textWithoutTags,
                });
                console.log("Response:", JSON.stringify(response.data.error));

                if (response.data.success) {
                    toast.add({
                        severity: "success",
                        summary: "Code validiert",
                        detail: "Der Python-Code ist syntaktisch korrekt",
                        life: 3000,
                    });
                } else {
                    toast.add({
                        severity: "error",
                        summary: "Code ungültig",
                        detail:
                            "Der Python-Code enthält Syntaxfehler: " +
                            "\n" +
                            response.data.error,
                        life: 5000,
                    });
                }
            } catch (error) {
                console.error(error);
                toast.add({
                    severity: "error",
                    summary: "Validierungsfehler",
                    detail: "Der Code enthält Syntaxfehler",
                    life: 5000,
                });
            } finally {
                validating.value = false;
            }
        };

        const submitTopology = async () => {
            if (!canSubmit.value) return;

            submitting.value = true;
            try {
                const topologyData = {
                    name: topologyName.value.trim(),
                    type: topologyType.value,
                    description: topologyDescription.value.trim(),
                    code: editorContent.value.trim(),
                    createdAt: new Date().toISOString(),
                };
                // TODO: Implement validation and error handling for topology description
                const response = await apiClient.post(
                    "topologies",
                    topologyData,
                );

                toast.add({
                    severity: "success",
                    summary: "Topologie erstellt",
                    detail: `${topologyData.name} wurde erfolgreich gespeichert`,
                    life: 5000,
                });

                resetForm();
            } catch (error) {
                console.error("Error submitting topology:", error);
                toast.add({
                    severity: "error",
                    summary: "Fehler beim Speichern",
                    detail:
                        error.response?.data?.message ||
                        "Ein unerwarteter Fehler ist aufgetreten",
                    life: 5000,
                });
            } finally {
                submitting.value = false;
            }
        };

        const resetForm = () => {
            editorContent.value = "";
            topologyName.value = "";
            topologyType.value = "";
            topologyDescription.value = "";
        };

        return {
            // Reactive data
            editorContent,
            topologyName,
            topologyType,
            topologyDescription,
            submitting,
            validating,
            topologyExamples,
            topologyTypes,
            responsiveOptions,

            // Computed
            canSubmit,

            // Methods
            selectExample,
            clearEditor,
            validateCode,
            submitTopology,
            resetForm,
        };
    },
};
</script>

<style scoped>
.topology-creator {
    width: 100%;
    min-height: 100vh;
    background: var(--nlb-bg-primary);
}

/* Header Section */
.header-section {
    background: var(--nlb-gradient-primary);
    padding: 3rem 2rem;
    color: var(--nlb-text-light);
    position: relative;
    overflow: hidden;
}

.header-section::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="75" cy="75" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="50" cy="10" r="0.5" fill="rgba(255,255,255,0.1)"/><circle cx="10" cy="60" r="0.5" fill="rgba(255,255,255,0.1)"/><circle cx="90" cy="40" r="0.5" fill="rgba(255,255,255,0.1)"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
    opacity: 0.3;
}

.header-content {
    position: relative;
    z-index: 1;
    max-width: 1200px;
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 2rem;
}

.header-text {
    flex: 1;
}

.main-title {
    font-size: 2.5rem;
    font-weight: 700;
    margin: 0 0 0.5rem 0;
    color: var(--nlb-text-light);
}

.subtitle {
    font-size: 1.1rem;
    margin: 0;
    opacity: 0.9;
    color: var(--nlb-text-light);
}

.header-stats {
    display: flex;
    gap: 1rem;
    flex-shrink: 0;
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
    color: var(--nlb-text-light);
}

.stat-label {
    font-size: 0.9rem;
    opacity: 0.8;
    color: var(--nlb-text-light);
}

/* Content Section */
.content-section {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
}

/* Section Headers */
.section-header {
    margin-bottom: 1.5rem;
}

.section-title {
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--nlb-text-primary);
    margin: 0 0 0.5rem 0;
}

.section-description {
    font-size: 1rem;
    color: var(--nlb-text-secondary);
    margin: 0;
}

/* Carousel Section */
.carousel-section {
    background: var(--nlb-bg-primary);
    border-radius: 16px;
    padding: 2rem;
    box-shadow: 0 20px 40px rgba(79, 70, 229, 0.15);
    margin-bottom: 2rem;
}

.topology-carousel {
    padding: 1rem 0;
}

.example-card {
    background: var(--nlb-bg-secondary);
    border: 2px solid var(--nlb-border-light);
    border-radius: 12px;
    padding: 1.5rem;
    margin: 0 0.5rem;
    cursor: pointer;
    transition: all 0.3s ease;
    height: 320px;
    display: flex;
    flex-direction: column;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.example-card:hover {
    border-color: var(--nlb-primary);
    box-shadow: 0 10px 25px rgba(102, 126, 234, 0.2);
    transform: translateY(-4px);
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.75rem;
}

.card-header h4 {
    margin: 0;
    color: var(--nlb-text-primary);
    font-size: 1.2rem;
    font-weight: 600;
}

.card-badge {
    background: var(--nlb-primary);
    color: var(--nlb-text-light);
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 500;
}

.card-description {
    color: var(--nlb-text-secondary);
    margin-bottom: 1rem;
    flex-grow: 1;
    line-height: 1.5;
}

.card-preview {
    background: var(--nlb-bg-tertiary);
    color: var(--nlb-text-primary);
    padding: 1rem;
    border-radius: 8px;
    margin-bottom: 1rem;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    font-size: 0.8rem;
    overflow: hidden;
    border: 1px solid var(--nlb-border-light);
}

.card-preview pre {
    margin: 0;
    white-space: pre-wrap;
    word-break: break-word;
}

/* Editor Section */
.editor-section {
    background: var(--nlb-bg-primary);
    border-radius: 16px;
    padding: 2rem;
    box-shadow: 0 20px 40px rgba(79, 70, 229, 0.15);
    margin-bottom: 2rem;
}

.section-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1.5rem;
}

.editor-actions {
    display: flex;
    gap: 0.75rem;
}

.topology-editor {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid var(--nlb-border-light);
}

/* Metadata Section */
.metadata-section {
    background: var(--nlb-bg-primary);
    border-radius: 16px;
    padding: 2rem;
    box-shadow: 0 20px 40px rgba(79, 70, 229, 0.15);
    margin-bottom: 2rem;
}

.metadata-form {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
}

.form-group {
    display: flex;
    flex-direction: column;
}

.form-group label {
    font-weight: 600;
    color: var(--nlb-text-primary);
    margin-bottom: 0.5rem;
    font-size: 0.9rem;
}

/* Action Section */
.action-section {
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
    padding: 2rem 0;
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

    .section-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 1rem;
    }

    .editor-actions {
        width: 100%;
        justify-content: flex-end;
    }
}

@media (max-width: 768px) {
    .content-section {
        padding: 1rem;
    }

    .header-section {
        padding: 2rem 1rem;
    }

    .main-title {
        font-size: 2rem;
    }

    .header-stats {
        flex-direction: column;
        gap: 0.75rem;
    }

    .stat-card {
        min-width: auto;
        padding: 1rem;
    }

    .form-row {
        grid-template-columns: 1fr;
    }

    .action-section {
        flex-direction: column;
    }

    .carousel-section,
    .editor-section,
    .metadata-section {
        padding: 1.5rem;
    }
}

@media (max-width: 480px) {
    .main-title {
        font-size: 1.75rem;
    }

    .subtitle {
        font-size: 1rem;
    }

    .stat-number {
        font-size: 1.5rem;
    }

    .example-card {
        height: 280px;
        padding: 1rem;
    }
}
</style>

