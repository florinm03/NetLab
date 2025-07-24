<template>
    <div class="pcap-analyzer">
        <!-- Modern Header Section -->
        <div class="header-section">
            <div class="header-content">
                <div class="header-text">
                    <h1 class="main-title">Traffic-Analyse</h1>
                    <p class="subtitle">
                        Analysieren Sie den Netzwerkverkehr und die Pakete einer
                        aufgezeichneten Umgebung
                    </p>
                </div>
                <div class="header-stats">
                    <div class="stat-card">
                        <div class="stat-number">{{ packets.length }}</div>
                        <div class="stat-label">Pakete</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">
                            {{ uniqueProtocols.length }}
                        </div>
                        <div class="stat-label">Protokolle</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Data Table Section -->
        <div class="table-section">
            <div class="table-header">
                <!-- <h2>Paket-Details</h2> -->
                
                <!-- PCAP Selection Dropdown -->
                <div class="pcap-selection">
                    <Dropdown
                        id="pcap-select"
                        v-model="selectedPcap"
                        :options="availablePcaps"
                        optionLabel="name"
                        optionValue="path"
                        placeholder="PCAP-Datei auswählen"
                        class="pcap-dropdown"
                        @change="loadSelectedPcap"
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

                <!-- Filter and Search -->
                <div class="search-box">
                    <i class="pi pi-search search-icon"></i>
                    <input
                        v-model="searchFilter"
                        type="text"
                        placeholder="Pakete durchsuchen..."
                        class="search-input"
                    />
                </div>
                <div class="filter-chips">
                    <button
                        v-for="protocol in topProtocols"
                        :key="protocol"
                        @click="toggleProtocolFilter(protocol)"
                        :class="[
                            'filter-chip',
                            {
                                active: selectedProtocols.includes(protocol),
                            },
                        ]"
                    >
                        {{ protocol.toUpperCase() }}
                    </button>
                    <button
                        v-if="selectedProtocols.length > 0"
                        @click="clearFilters"
                        class="clear-filter"
                    >
                        ✕ Filter löschen
                    </button>
                </div>

                <div class="table-actions">
                    <span class="results-count"
                        >{{ filteredPackets.length }} von
                        {{ packets.length }} Paketen (Seite
                        {{ currentPage + 1 }} von {{ totalPages }})</span
                    >
                </div>
            </div>

            <DataTable
                class="modern-table"
                :value="filteredPackets"
                dataKey="no"
                rowHover
                responsiveLayout="scroll"
                :expandedRows="expandedRows"
                @row-toggle="(e) => (expandedRows = e.data)"
                expandableRows
                scrollable
                scrollHeight="70vh"
                selectionMode="single"
                :loading="loading"
                v-model:selection="selectedRow"
                stripedRows
                :paginator="true"
                :rows="rowsPerPage"
                :totalRecords="filteredPackets.length"
                v-model:first="first"
                @page="onPageChange"
                paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
                currentPageReportTemplate="Zeige {first} bis {last} von {totalRecords} Einträgen"
                :rowsPerPageOptions="[25, 50, 100, 200]"
            >
                <Column expander style="width: 3rem" />
                <Column field="no" header="Nr." style="width: 4rem" sortable>
                    <template #body="slotProps">
                        <span class="packet-number">{{
                            slotProps.data.no
                        }}</span>
                    </template>
                </Column>
                <Column
                    field="time"
                    header="Zeit"
                    style="width: 10rem"
                    sortable
                >
                    <template #body="slotProps">
                        <span class="time-stamp">{{
                            slotProps.data.time
                        }}</span>
                    </template>
                </Column>
                <Column
                    field="src"
                    header="Quelle"
                    style="width: 12rem"
                    sortable
                >
                    <template #body="slotProps">
                        <span class="ip-address">{{ slotProps.data.src }}</span>
                    </template>
                </Column>
                <Column field="dst" header="Ziel" style="width: 12rem" sortable>
                    <template #body="slotProps">
                        <span class="ip-address">{{ slotProps.data.dst }}</span>
                    </template>
                </Column>
                <Column
                    field="proto"
                    header="Protokoll"
                    style="width: 7rem"
                    sortable
                >
                    <template #body="slotProps">
                        <span
                            :class="[
                                'protocol-badge',
                                getProtocolClass(slotProps.data.proto),
                            ]"
                        >
                            {{ slotProps.data.proto.toUpperCase() }}
                        </span>
                    </template>
                </Column>
                <Column field="len" header="Länge" style="width: 5rem" sortable>
                    <template #body="slotProps">
                        <span class="packet-length">{{
                            slotProps.data.len
                        }}</span>
                    </template>
                </Column>
                <Column field="info" header="Informationen" sortable>
                    <template #body="slotProps">
                        <span class="packet-info">{{
                            slotProps.data.info
                        }}</span>
                    </template>
                </Column>

                <template #expansion="slotProps">
                    <div class="packet-details">
                        <div class="details-header">
                            <h3>Paket Details - #{{ slotProps.data.no }}</h3>
                            <button
                                @click="copyPacketData(slotProps.data)"
                                class="copy-btn"
                            >
                                <i class="pi pi-clipboard"></i>
                                Kopieren
                            </button>
                        </div>
                        <div class="json-viewer">
                            <pre>{{ prettyPrint(slotProps.data.raw) }}</pre>
                        </div>
                    </div>
                </template>

                <template #loading>
                    <div class="loading-container">
                        <div class="loading-spinner"></div>
                        <p>Lade Paket-Daten...</p>
                    </div>
                </template>
            </DataTable>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, computed, watch, inject } from "vue";
import DataTable from "primevue/datatable";
import Column from "primevue/column";
import Dropdown from "primevue/dropdown";
import { useToast } from "primevue/usetoast";

const apiClient = inject('axios');

const toast = useToast();
const packets = ref([]);
const expandedRows = ref({});
const selectedRow = ref(null);
const loading = ref(true);
const searchFilter = ref("");
const selectedProtocols = ref([]);

// PCAP Selection
const selectedPcap = ref(null);
const availablePcaps = ref([
    {
        name: "Mesh Demo",
        path: "/src/pcap_demos/json/mesh.json",
        description: "Mesh-Topologie Demo PCAP-Datei",
        type: "demo"
    },
    {
        name: "Ring Demo",
        path: "/src/pcap_demos/json/ring.json",
        description: "Ring-Topologie Demo PCAP-Datei",
        type: "demo"
    },
    {
        name: "Star Demo",
        path: "/src/pcap_demos/json/star.json",
        description: "Stern-Topologie Demo PCAP-Datei",
        type: "demo"
    },
    {
        name: "Tree Demo",
        path: "/src/pcap_demos/json/tree.json",
        description: "Baum-Topologie Demo PCAP-Datei",
        type: "demo"
    }
]);

const rowsPerPage = ref(50);
const first = ref(0);
const currentPage = ref(0);

const prettyPrint = (obj) => JSON.stringify(obj, null, 2);

const filteredPackets = computed(() => {
    let filtered = packets.value;

    if (searchFilter.value) {
        const term = searchFilter.value.toLowerCase();
        filtered = filtered.filter(
            (packet) =>
                packet.src.toLowerCase().includes(term) ||
                packet.dst.toLowerCase().includes(term) ||
                packet.info.toLowerCase().includes(term) ||
                packet.proto.toLowerCase().includes(term),
        );
    }

    if (selectedProtocols.value.length > 0) {
        filtered = filtered.filter((packet) =>
            selectedProtocols.value.includes(packet.proto.toLowerCase()),
        );
    }

    return filtered;
});

const totalPages = computed(() => {
    return Math.ceil(filteredPackets.value.length / rowsPerPage.value);
});

const uniqueProtocols = computed(() => {
    const protocols = new Set(packets.value.map((p) => p.proto.toLowerCase()));
    return Array.from(protocols).filter((p) => p);
});

const topProtocols = computed(() => {
    const protocolCounts = {};
    packets.value.forEach((packet) => {
        const proto = packet.proto.toLowerCase();
        if (proto) {
            protocolCounts[proto] = (protocolCounts[proto] || 0) + 1;
        }
    });

    return Object.entries(protocolCounts)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 8)
        .map(([proto]) => proto);
});

// Watch for filter changes to reset pagination
watch(
    [searchFilter, selectedProtocols],
    () => {
        resetPagination();
    },
    { deep: true },
);

// Methods
const toggleProtocolFilter = (protocol) => {
    const index = selectedProtocols.value.indexOf(protocol);
    if (index > -1) {
        selectedProtocols.value.splice(index, 1);
    } else {
        selectedProtocols.value.push(protocol);
    }
};

const clearFilters = () => {
    selectedProtocols.value = [];
    searchFilter.value = "";
};

const resetPagination = () => {
    first.value = 0;
    currentPage.value = 0;
};

const onPageChange = (event) => {
    first.value = event.first;
    currentPage.value = event.page;
};

const getProtocolClass = (protocol) => {
    const proto = protocol.toLowerCase();
    if (["http", "https", "http2"].includes(proto)) return "protocol-http";
    if (["tcp", "udp"].includes(proto)) return "protocol-transport";
    if (["dns"].includes(proto)) return "protocol-dns";
    if (["icmp", "igmp", "arp", "ospf", "icmpv6"].includes(proto)) return "protocol-network";
    if (["tls", "ssl"].includes(proto)) return "protocol-security";
    return "protocol-other";
};

const copyPacketData = async (packet) => {
    try {
        await navigator.clipboard.writeText(prettyPrint(packet.raw));
        toast.add({
            severity: "success",
            summary: "Erfolgreich kopiert",
            detail: "Die Paketdaten befinden sich in der Zwischenablage.",
            life: 3000,
        });
    } catch (err) {
        console.error("Failed to copy packet data:", err);
    }
};

// Load PCAP data from selected file
const loadPcapData = async (filePath) => {
    loading.value = true;
    try {
        const isDatabasePcap = filePath.startsWith('/pcap/');
        
        let resp;
        if (isDatabasePcap) {
            const pcapId = filePath.split('/')[2]; // Get ID from /pcap/{id}/download
            const jsonResponse = await apiClient.get(`/pcap/${pcapId}/json`);
            
            if (jsonResponse.data.status === 'success') {
                const raw = jsonResponse.data.data;
                
                packets.value = raw.map((pkt) => {
                    const frameNumber = pkt["frame.number"] || "";
                    const relTime = pkt["frame.time_relative"] || "";
                    const ipSrc = pkt["ip.src"] || pkt["ipv6.src"] || "";
                    const ipDst = pkt["ip.dst"] || pkt["ipv6.dst"] || "";
                    const frameProtocols = pkt["frame.protocols"] || "";
                    const frameLen = pkt["frame.len"] || "";
                    const wsColInfo = pkt["_ws.col.Info"] || pkt["_ws.col.info"] || "";

                    const topProto = extractTopProtocol(frameProtocols);

                    return {
                        no: frameNumber,
                        time: relTime,
                        src: ipSrc,
                        dst: ipDst,
                        proto: topProto,
                        len: frameLen,
                        info: wsColInfo,
                        raw: pkt,
                    };
                });

                clearFilters();
                resetPagination();

                toast.add({
                    severity: "success",
                    summary: "PCAP geladen",
                    detail: `${packets.value.length} Pakete erfolgreich geladen.`,
                    life: 3000,
                });
                loading.value = false;
                return;
            } else {
                throw new Error(jsonResponse.data.message || 'Failed to load PCAP JSON data');
            }
        } else {
            // Regular JSON PCAP files
            resp = await fetch(filePath);
            if (!resp.ok) {
                throw new Error(
                    `Failed to fetch packets: ${resp.status} ${resp.statusText}`,
                );
            }
        }
        
        const raw = await resp.json();

        packets.value = raw.map((pkt) => {
            const frameNumber = pkt["frame.number"] || "";
            const relTime = pkt["frame.time_relative"] || "";
            // Prefer IPv4, then IPv6, then fallback to empty string
            const ipSrc = pkt["ip.src"] || pkt["ipv6.src"] || "";
            const ipDst = pkt["ip.dst"] || pkt["ipv6.dst"] || "";
            const frameProtocols = pkt["frame.protocols"] || "";
            const frameLen = pkt["frame.len"] || "";
            const wsColInfo = pkt["_ws.col.Info"] || pkt["_ws.col.info"] || "";

            const topProto = extractTopProtocol(frameProtocols);

            return {
                no: frameNumber,
                time: relTime,
                src: ipSrc,
                dst: ipDst,
                proto: topProto,
                len: frameLen,
                info: wsColInfo,
                raw: pkt,
            };
        });

        clearFilters();
        resetPagination();

        toast.add({
            severity: "success",
            summary: "PCAP geladen",
            detail: `${packets.value.length} Pakete erfolgreich geladen.`,
            life: 3000,
        });
    } catch (error) {
        console.error("Error loading packet data:", error);
        toast.add({
            severity: "error",
            summary: "Fehler",
            detail: "PCAP-Datei konnte nicht geladen werden.",
            life: 5000,
        });
    } finally {
        loading.value = false;
    }
};

// Handle PCAP selection change
const loadSelectedPcap = () => {
    if (selectedPcap.value) {
        loadPcapData(selectedPcap.value);
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
                    path: `/pcap/${pcap.id}/download`,
                    description: `Erstellt am ${formattedDate} - ${pcap.topology_type} Topologie mit ${pcap.node_count} Knoten`,
                    type: "saved",
                    isDatabase: true,
                    pcapId: pcap.id,
                    metadata: pcap.metadata_json ? JSON.parse(pcap.metadata_json) : null,
                    created_at: pcap.created_at,
                    hasJsonData: !!pcap.pcap_json
                };
            });
            
            availablePcaps.value = [...availablePcaps.value, ...dbPcaps];
        }
    } catch (error) {
        console.error("Error loading PCAPs from database:", error);
    }
};

// Extract top protocol from frame.protocols string
const extractTopProtocol = (protocolsStr) => {
    if (!protocolsStr) return "";
    
    const protocols = protocolsStr.split(":");
    const lowerProtocols = [
        "sll",
        "ethertype",
        "eth",
        "frame",
        "ip",
        "ipv6",
        "data"
    ];
    
    for (let i = protocols.length - 1; i >= 0; i--) {
        const proto = protocols[i].toLowerCase();
        if (!lowerProtocols.includes(proto)) {
            return proto;
        }
    }
    
    return protocols[protocols.length - 1] || "";
};

// Format time display
const formatTime = (timeStr) => {
    if (!timeStr) return "";
    
    try {
        // Clean up the time string - remove extra spaces and timezone
        const cleanedTimeStr = timeStr
            .replace(/\s+/g, ' ') // Replace multiple spaces with single space
            .replace(/\s+CEST$/, '') // Remove CEST timezone
            .replace(/\s+CET$/, ''); // Remove CET timezone
        
        const date = new Date(cleanedTimeStr);
        
        if (isNaN(date.getTime())) {
            const timeMatch = timeStr.match(/(\d{1,2}:\d{2}:\d{2}\.\d+)/);
            if (timeMatch) {
                return timeMatch[1];
            }
            return timeStr;
        }
        
        return date.toLocaleTimeString('de-DE') + "." + 
               date.getMilliseconds().toString().padStart(3, "0");
    } catch (e) {
        const timeMatch = timeStr.match(/(\d{1,2}:\d{2}:\d{2}\.\d+)/);
        if (timeMatch) {
            return timeMatch[1];
        }
        return timeStr;
    }
};

onMounted(async () => {
    const urlParams = new URLSearchParams(window.location.search);
    const topologyParam = urlParams.get('topology');
    
    if (topologyParam) {
        const matchingPcap = availablePcaps.value.find(pcap => pcap.name === topologyParam);
        if (matchingPcap) {
            selectedPcap.value = matchingPcap.path;
        } else {
            selectedPcap.value = availablePcaps.value[0].path;
        }
    } else {
        selectedPcap.value = availablePcaps.value[0].path;
    }
    
    await loadPcapsFromDatabase();
    
    await loadPcapData(selectedPcap.value);
});
</script>

<style scoped>
.pcap-analyzer {
    min-height: 93vh;
    background: var(--nlb-gradient-primary);
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

.header-text {
    width: 50vw;
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
    max-width: 850px;
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

.pcap-name {
    font-weight: 600;
    color: var(--nlb-text-primary);
}

.pcap-description {
    font-size: 0.8rem;
    color: var(--nlb-text-secondary);
}

/* Controls Section */

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

.clear-filter {
    padding: 0.5rem 1rem;
    background: var(--nlb-error);
    color: var(--nlb-text-light);
    border: none;
    border-radius: 20px;
    font-size: 0.875rem;
    cursor: pointer;
    transition: all 0.2s ease;
}

.clear-filter:hover {
    background: var(--nlb-error-dark);
}

/* Table Section */
.table-section {
    background: var(--nlb-bg-primary);
    border-radius: 0 0 16px 16px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    overflow: hidden;
}

.table-header {
    padding: 1.5rem 2rem;
    border-bottom: 1px solid var(--nlb-border-light);
    display: flex;
    flex-direction: row;
    justify-items: space-between;
    align-items: center;
    gap: 1.5rem;
}

.table-title-section {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.table-title-section h2 {
    margin: 0;
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--nlb-text-primary);
}

.results-count {
    color: var(--nlb-text-secondary);
    font-size: 0.875rem;
}

.table-controls {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.search-box {
    position: relative;
    max-width: 400px;
}

.search-icon {
    position: absolute;
    left: 1rem;
    top: 50%;
    transform: translateY(-50%);
    color: var(--nlb-text-secondary);
    font-size: 1.1rem;
}

.search-input {
    width: 100%;
    padding: 0.75rem 1rem 0.75rem 3rem;
    border: 2px solid var(--nlb-border-light);
    border-radius: 12px;
    font-size: 1rem;
    background: var(--nlb-bg-primary);
    transition: all 0.2s ease;
}

.search-input:focus {
    outline: none;
    border-color: var(--nlb-primary);
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.filter-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
    align-items: center;
}

/* Modern Table Styling */
.modern-table {
    --primary-color: var(--nlb-primary);
    --surface-ground: var(--nlb-bg-primary);
    --text-color: var(--nlb-text-primary);
}

.modern-table :deep(.p-datatable-header) {
    background: var(--nlb-bg-secondary);
    border-bottom: 2px solid var(--nlb-border-light);
    padding: 1rem;
}

.modern-table :deep(.p-datatable-thead > tr > th) {
    background: var(--nlb-bg-secondary);
    color: var(--nlb-text-primary);
    font-weight: 600;
    font-size: 0.875rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding: 1rem 0.75rem;
    border-bottom: 2px solid var(--nlb-border-light);
}

.modern-table :deep(.p-datatable-tbody > tr) {
    transition: all 0.2s ease;
}

.modern-table :deep(.p-datatable-tbody > tr:hover) {
    background-color: var(--nlb-bg-tertiary) !important;
    transform: translateY(-1px);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.modern-table :deep(.p-datatable-tbody > tr > td) {
    padding: 0.875rem 0.75rem;
    border-bottom: 1px solid var(--nlb-bg-tertiary);
}

/* Pagination Styling */
.modern-table :deep(.p-paginator) {
    background: var(--nlb-bg-secondary);
    border-top: 1px solid var(--nlb-border-light);
    padding: 1rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 1rem;
}

.modern-table :deep(.p-paginator .p-paginator-pages) {
    display: flex;
    align-items: center;
    gap: 0.25rem;
}

.modern-table :deep(.p-paginator .p-paginator-page),
.modern-table :deep(.p-paginator .p-paginator-first),
.modern-table :deep(.p-paginator .p-paginator-prev),
.modern-table :deep(.p-paginator .p-paginator-next),
.modern-table :deep(.p-paginator .p-paginator-last) {
    background: var(--nlb-bg-primary);
    border: 1px solid var(--nlb-border-light);
    color: var(--nlb-text-secondary);
    min-width: 2.5rem;
    height: 2.5rem;
    display: flex;
    align-items: center;
    justify-content: center;
    text-decoration: none;
    border-radius: 6px;
    font-size: 0.875rem;
    transition: all 0.2s ease;
}

.modern-table :deep(.p-paginator .p-paginator-page:hover),
.modern-table :deep(.p-paginator .p-paginator-first:hover),
.modern-table :deep(.p-paginator .p-paginator-prev:hover),
.modern-table :deep(.p-paginator .p-paginator-next:hover),
.modern-table :deep(.p-paginator .p-paginator-last:hover) {
    background: var(--nlb-primary);
    border-color: var(--nlb-primary);
    color: var(--nlb-text-light);
}

.modern-table :deep(.p-paginator .p-paginator-page.p-highlight) {
    background: var(--nlb-primary);
    border-color: var(--nlb-primary);
    color: var(--nlb-text-light);
}

.modern-table :deep(.p-paginator .p-paginator-current) {
    color: var(--nlb-text-primary);
    font-size: 0.875rem;
    font-weight: 500;
}

.modern-table :deep(.p-paginator .p-dropdown) {
    background: var(--nlb-bg-primary);
    border: 1px solid var(--nlb-border-light);
    border-radius: 6px;
    padding: 0.5rem;
    font-size: 0.875rem;
    color: var(--nlb-text-primary);
    min-width: 5rem;
}

.modern-table :deep(.p-paginator .p-dropdown:hover) {
    border-color: var(--nlb-primary);
}

.modern-table :deep(.p-paginator .p-dropdown .p-dropdown-label) {
    padding: 0.25rem 0.5rem;
}

.modern-table :deep(.p-paginator .p-dropdown .p-dropdown-trigger) {
    width: 2rem;
    color: var(--nlb-text-secondary);
}

/* Protocol badges */
.protocol-badge {
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
}

.protocol-http {
    background: var(--nlb-protocol-http-bg);
    color: var(--nlb-protocol-http);
}
.protocol-transport {
    background: var(--nlb-protocol-transport-bg);
    color: var(--nlb-protocol-transport);
}
.protocol-dns {
    background: var(--nlb-protocol-dns-bg);
    color: var(--nlb-protocol-dns);
}
.protocol-network {
    background: var(--nlb-protocol-network-bg);
    color: var(--nlb-protocol-network);
}
.protocol-security {
    background: var(--nlb-protocol-security-bg);
    color: var(--nlb-protocol-security);
}
.protocol-other {
    background: var(--nlb-protocol-other-bg);
    color: var(--nlb-protocol-other);
}

/* Packet details */
.packet-details {
    padding: 1.5rem;
    background: var(--nlb-bg-secondary);
    border-top: 1px solid var(--nlb-border-light);
}

.details-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
}

.details-header h3 {
    margin: 0;
    color: var(--nlb-text-primary);
    font-size: 1.1rem;
}

.copy-btn {
    padding: 0.5rem 1rem;
    background: var(--nlb-primary);
    color: var(--nlb-text-light);
    border: none;
    border-radius: 8px;
    font-size: 0.875rem;
    cursor: pointer;
    transition: background 0.2s ease;
}

.copy-btn:hover {
    background: var(--nlb-primary-dark);
}

.json-viewer {
    background: var(--nlb-bg-primary);
    border: 1px solid var(--nlb-border-light);
    border-radius: 8px;
    overflow: hidden;
}

.json-viewer pre {
    margin: 0;
    padding: 1rem;
    font-size: 0.8rem;
    font-family: "Monaco", "Consolas", monospace;
    line-height: 1.5;
    overflow-x: auto;
    white-space: pre-wrap;
    color: var(--nlb-text-primary);
}

/* Data styling */
.packet-number {
    font-weight: 600;
    color: var(--nlb-primary);
}

.time-stamp {
    font-family: monospace;
    font-size: 0.875rem;
    color: var(--nlb-text-secondary);
}

.ip-address {
    font-family: monospace;
    font-size: 0.875rem;
    font-weight: 500;
}

.packet-length {
    font-family: monospace;
    font-size: 0.875rem;
    color: var(--nlb-text-secondary);
}

.packet-info {
    font-size: 0.875rem;
    line-height: 1.4;
}

/* Loading state */
.loading-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 3rem;
    color: var(--nlb-text-secondary);
}

.loading-spinner {
    width: 40px;
    height: 40px;
    border: 3px solid var(--nlb-border-light);
    border-top: 3px solid var(--nlb-primary);
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 1rem;
}

@keyframes spin {
    0% {
        transform: rotate(0deg);
    }
    100% {
        transform: rotate(360deg);
    }
}

/* PCAP Dropdown Styling */
.pcap-option {
    padding: 0.5rem 0;
}

.pcap-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.25rem;
}

.pcap-name {
    font-weight: 600;
    color: var(--nlb-text-primary);
    font-size: 0.9rem;
}

.pcap-badge {
    padding: 0.2rem 0.5rem;
    border-radius: 6px;
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    background: var(--nlb-primary);
    color: var(--nlb-text-light);
}

.pcap-badge.demo {
    background: var(--nlb-accent);
    color: var(--nlb-text-light);
}

.pcap-description {
    font-size: 0.8rem;
    color: var(--nlb-text-secondary);
    line-height: 1.3;
}

/* Responsive design */
@media (max-width: 768px) {
    .header-content {
        flex-direction: column;
        text-align: center;
    }

    .main-title {
        font-size: 2rem;
    }

    .header-stats {
        justify-content: center;
    }

    .table-header {
        gap: 1rem;
        flex-wrap: wrap;
    }

    .pcap-selection {
        flex-direction: column;
        align-items: flex-start;
        gap: 0.5rem;
        width: 100%;
    }

    .pcap-dropdown {
        min-width: 100%;
    }

    .table-title-section {
        flex-direction: column;
        gap: 0.5rem;
        text-align: center;
    }

    .table-controls {
        gap: 1rem;
    }

    .filter-chips {
        justify-content: center;
    }

    .modern-table :deep(.p-paginator) {
        flex-direction: column;
        text-align: center;
        gap: 1rem;
    }

    .modern-table :deep(.p-paginator .p-paginator-pages) {
        justify-content: center;
    }
}
</style>