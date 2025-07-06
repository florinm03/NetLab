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
                <h2>Paket-Details</h2>
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
import { ref, onMounted, computed, watch } from "vue";
import DataTable from "primevue/datatable";
import Column from "primevue/column";
import { useToast } from "primevue/usetoast";

const toast = useToast();
const packets = ref([]);
const expandedRows = ref({});
const selectedRow = ref(null);
const loading = ref(true);
const searchFilter = ref("");
const selectedProtocols = ref([]);

// Pagination properties
const rowsPerPage = ref(50);
const first = ref(0);
const currentPage = ref(0);

const prettyPrint = (obj) => JSON.stringify(obj, null, 2);

// Computed properties for filtering and statistics
const filteredPackets = computed(() => {
    let filtered = packets.value;

    // Filter by search term
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

    // Filter by selected protocols
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
    if (["icmp", "igmp", "arp"].includes(proto)) return "protocol-network";
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

// protocol extraction and packet parsing logic
const findProperty = (obj, propName) => {
    if (!obj || typeof obj !== "object") return null;
    const lowerPropName = propName.toLowerCase();
    const key = Object.keys(obj).find((k) => k.toLowerCase() === lowerPropName);
    return key ? obj[key] : null;
};

const extractProtocols = (frame) => {
    const protocolsStr = findProperty(frame, "frame.protocols");
    if (!protocolsStr) return [];
    return protocolsStr.split(":");
};

const getTopProtocol = (protocols) => {
    if (!protocols || protocols.length === 0) return "";
    const lowerProtocols = [
        "sll",
        "ethertype",
        "eth",
        "frame",
        "ip",
        "ipv6",
        "data",
    ];
    for (let i = protocols.length - 1; i >= 0; i--) {
        const proto = protocols[i].toLowerCase();
        if (!lowerProtocols.includes(proto)) {
            return proto;
        }
    }
    return protocols[protocols.length - 1];
};

const extractHttpInfo = (layers) => {
    const http = layers.http || layers.http2;
    if (!http) return "";

    const requestMethod = http["http.request.method"];
    if (requestMethod) {
        const uri =
            http["http.request.full_uri"] || http["http.request.uri"] || "";
        return `${requestMethod} ${uri}`;
    }

    const responseCode = http["http.response.code"];
    if (responseCode) {
        const phrase = http["http.response.phrase"] || "";
        return `Status: ${responseCode} ${phrase}`;
    }

    return "HTTP-Daten";
};

const extractDnsInfo = (layers) => {
    const dns = layers.dns;
    if (!dns) return "";

    const queryName = dns["dns.qry.name"];
    if (queryName) {
        const queryType = dns["dns.qry.type"];
        return `Standard query ${queryType} ${queryName}`;
    }

    const respName = dns["dns.resp.name"];
    if (respName) {
        const answers = dns["dns.count.answers"];
        return `Standard query response ${respName} with ${answers} answers`;
    }

    return "DNS-Paket";
};

const extractArpInfo = (layers) => {
    const arp = layers.arp;
    if (!arp) return "";
    const opcode = arp["arp.opcode"];
    const srcIp = arp["arp.src.proto_ipv4"];
    const dstIp = arp["arp.dst.proto_ipv4"];
    const srcMac = arp["arp.src.hw_mac"];

    if (opcode === "1") {
        // Request
        return `Who has ${dstIp}? Tell ${srcIp}`;
    }
    if (opcode === "2") {
        // Reply
        return `${srcIp} is at ${srcMac}`;
    }
    return `ARP Opcode: ${opcode}`;
};

const extractTcpInfo = (layers) => {
    const tcp = layers.tcp;
    if (!tcp) return "";

    const srcPort = tcp["tcp.srcport"];
    const dstPort = tcp["tcp.dstport"];
    const flagsTree = tcp["tcp.flags_tree"];

    let flags = [];
    if (flagsTree) {
        if (flagsTree["tcp.flags.syn"] === "1") flags.push("SYN");
        if (flagsTree["tcp.flags.ack"] === "1") flags.push("ACK");
        if (flagsTree["tcp.flags.fin"] === "1") flags.push("FIN");
        if (flagsTree["tcp.flags.reset"] === "1") flags.push("RST");
        if (flagsTree["tcp.flags.push"] === "1") flags.push("PSH");
    }

    return `${srcPort} → ${dstPort} [${flags.join(", ")}]`;
};

// --- Hauptfunktion zur Info-Extraktion ---

const extractPacketInfo = (layers, topProto) => {
    switch (topProto.toLowerCase()) {
        case "http":
        case "http2":
            return extractHttpInfo(layers);
        case "dns":
            return extractDnsInfo(layers);
        case "arp":
            return extractArpInfo(layers);
        case "tcp":
            return extractTcpInfo(layers);
        case "udp":
            const udp = layers.udp;
            if (udp) return `${udp["udp.srcport"]} → ${udp["udp.dstport"]}`;
            return "UDP-Paket";
        case "icmp":
            const icmp = layers.icmp;
            if (icmp) {
                const type = icmp["icmp.type"];
                const code = icmp["icmp.code"];
                if (type === "8") return "Echo (ping) request";
                if (type === "0") return "Echo (ping) reply";
                return `Type ${type}, Code ${code}`;
            }
            return "ICMP-Paket";
        case "tls":
            const tls = layers.tls;
            if (tls) {
                const contentType = tls["tls.record.content_type"];
                if (contentType === "22") return "Client Hello / Server Hello";
                if (contentType === "23") return "Application Data";
                return `TLS Record, Content Type: ${contentType}`;
            }
            return "TLS-Paket";
        default:
            return `Paket für Protokoll ${topProto.toUpperCase()}`;
    }
};

onMounted(async () => {
    loading.value = true;
    try {
        const resp = await fetch("/src/packets.json");
        if (!resp.ok) {
            throw new Error(
                `Failed to fetch packets: ${resp.status} ${resp.statusText}`,
            );
        }
        const raw = await resp.json();

        packets.value = raw.map((pkt) => {
            const layers = pkt._source.layers;
            const frame = layers.frame || {};
            const eth = layers.eth || {};
            const ip = layers.ip || layers.ipv6 || {};

            const protocols = extractProtocols(frame);
            const topProto = getTopProtocol(protocols);

            let timeDisplay =
                frame["frame.time_relative"] || frame["frame.time"] || "";
            if (timeDisplay && !frame["frame.time_relative"]) {
                try {
                    const date = new Date(timeDisplay);
                    timeDisplay =
                        date.toLocaleTimeString() +
                        "." +
                        date.getMilliseconds().toString().padStart(3, "0");
                } catch (e) {
                    // Behalte Originalwert bei Fehler
                }
            }

            let source = ip["ip.src"] || ip["ipv6.src"] || "";
            let dest = ip["ip.dst"] || ip["ipv6.dst"] || "";

            if (layers.sll && !source) {
                source = layers.sll["sll.src.eth"] || "";
            }

            if (!source && eth["eth.src"]) {
                source = eth["eth.src"];
            }
            if (!dest && eth["eth.dst"]) {
                dest = eth["eth.dst"];
            }

            if (layers.arp) {
                const arpSrc = layers.arp["arp.src.proto_ipv4"];
                const arpDst = layers.arp["arp.dst.proto_ipv4"];
                if (arpSrc) source = arpSrc;
                if (arpDst) dest = arpDst;
            }

            return {
                no: frame["frame.number"] || "",
                time: timeDisplay,
                src: source,
                dst: dest,
                proto: topProto || "",
                len: frame["frame.len"] || "",
                info: extractPacketInfo(layers, topProto),
                raw: layers,
            };
        });
    } catch (error) {
        console.error("Error loading packet data:", error);
    } finally {
        loading.value = false;
    }
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
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
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
