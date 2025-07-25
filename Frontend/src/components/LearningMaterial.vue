<template>
    <div class="topology-card">
        <div class="header-section">
            <h1 class="page-title">Netzwerk-Topologien</h1>
            <p class="page-description">
                Wählen Sie eine Topologie aus, um mehr darüber zu erfahren
            </p>
        </div>
        <Carousel
            :value="topologies"
            :numVisible="computedNumVisible"
            :numScroll="1"
            :responsiveOptions="responsiveOptions"
            :circular="shouldBeCircular"
            :showNavigators="shouldShowNavigators"
            class="carousel"
        >
            <template #item="{ data: topology }">
                <div
                    class="topology-item"
                    :class="{ selected: selectedTopology === topology.key }"
                    @click="selectTopology(topology.key)"
                >
                    <div class="topology-icon">{{ topology.icon }}</div>
                    <div class="topology-name">{{ topology.name }}</div>
                    <div class="topology-brief">{{ topology.brief }}</div>
                </div>
            </template>
        </Carousel>

        <div v-if="selectedTopology" class="topology-details active">
            <div class="details-title">
                {{ topologyData[selectedTopology].name }}
            </div>

            <div class="details-section">
                <h4>Beschreibung</h4>
                <p>{{ topologyData[selectedTopology].description }}</p>
            </div>

            <div class="details-section">
                <h4>Vorteile</h4>
                <ul class="advantages-list">
                    <li
                        v-for="advantage in topologyData[selectedTopology]
                            .advantages"
                        :key="advantage"
                    >
                        {{ advantage }}
                    </li>
                </ul>
            </div>

            <div class="details-section">
                <h4>Nachteile</h4>
                <ul class="disadvantages-list">
                    <li
                        v-for="disadvantage in topologyData[selectedTopology]
                            .disadvantages"
                        :key="disadvantage"
                    >
                        {{ disadvantage }}
                    </li>
                </ul>
            </div>

            <div class="details-section">
                <h4>Verwendung</h4>
                <p>{{ topologyData[selectedTopology].usage }}</p>
            </div>

            <div class="details-section">
                <Button 
                    label="Traffic-Analyse anzeigen" 
                    icon="pi pi-chart-line" 
                    class="p-button-primary"
                    @click="navigateToPcapTable"
                />
            </div>
        </div>

        <div v-if="!selectedTopology" class="prompt-text">
            Klicken Sie auf eine Topologie oben, um detaillierte Informationen
            zu sehen
        </div>
    </div>
</template>

<script>
import Carousel from 'primevue/carousel';
import Button from 'primevue/button';

export default {
    name: "NetworkTopologies",
    components: {
        Carousel,
        Button
    },
    data() {
        return {
            selectedTopology: null,
            currentNumVisible: 6,
            topologies: [
                {
                    key: "bus",
                    name: "Bus-Topologie",
                    brief: "Linear verbunden",
                    icon: "🚌",
                },
                {
                    key: "star",
                    name: "Stern-Topologie",
                    brief: "Zentral verbunden",
                    icon: "⭐",
                },
                {
                    key: "ring",
                    name: "Ring-Topologie",
                    brief: "Kreisförmig verbunden",
                    icon: "🔄",
                },
                {
                    key: "mesh",
                    name: "Mesh-Topologie",
                    brief: "Vollvernetzt",
                    icon: "🕸️",
                },
                {
                    key: "tree",
                    name: "Baum-Topologie",
                    brief: "Hierarchisch verbunden",
                    icon: "🌳",
                },
                {
                    key: "hybrid",
                    name: "Hybrid-Topologie",
                    brief: "Kombinierte Strukturen",
                    icon: "🔀",
                },
            ],
            topologyData: {
                bus: {
                    name: "Bus-Topologie",
                    description:
                        "Bei der Bus-Topologie sind alle Geräte über ein gemeinsames Übertragungsmedium (Bus) miteinander verbunden. Die Daten werden an alle Geräte gesendet, aber nur das Zielgerät verarbeitet sie.",
                    advantages: [
                        "Einfache Installation und Konfiguration",
                        "Kostengünstig durch wenig Verkabelung",
                        "Einfache Erweiterung um neue Geräte",
                        "Geringer Kabelbedarf",
                    ],
                    disadvantages: [
                        "Ausfall des Hauptkabels betrifft das gesamte Netzwerk",
                        "Schwierige Fehlersuche",
                        "Begrenzte Übertragungsgeschwindigkeit",
                        "Kollisionen bei gleichzeitiger Übertragung",
                    ],
                    usage: "Früher in Ethernet-Netzwerken (10Base2, 10Base5), heute hauptsächlich in industriellen Anwendungen und CAN-Bus-Systemen in Fahrzeugen.",
                },
                star: {
                    name: "Stern-Topologie",
                    description:
                        "In der Stern-Topologie sind alle Geräte direkt mit einem zentralen Knotenpunkt (Switch oder Hub) verbunden. Alle Kommunikation läuft über diesen zentralen Punkt.",
                    advantages: [
                        "Hohe Zuverlässigkeit - Ausfall eines Geräts betrifft andere nicht",
                        "Einfache Fehlersuche und Wartung",
                        "Gute Performance durch dedizierte Verbindungen",
                        "Einfache Rekonfiguration und Erweiterung",
                    ],
                    disadvantages: [
                        "Zentraler Punkt ist Single Point of Failure",
                        "Höhere Kosten durch zusätzliche Hardware",
                        "Mehr Kabel erforderlich",
                        "Begrenzt durch Anzahl der Ports am zentralen Gerät",
                    ],
                    usage: "Die häufigste Topologie in modernen LAN-Netzwerken, verwendet in Büros, Heimen und Rechenzentren mit Switches als zentralem Element.",
                },
                ring: {
                    name: "Ring-Topologie",
                    description:
                        "Bei der Ring-Topologie sind die Geräte in einem geschlossenen Kreis miteinander verbunden. Daten werden in eine Richtung von Gerät zu Gerät weitergeleitet, bis sie ihr Ziel erreichen.",
                    advantages: [
                        "Gleichmäßige Netzwerkleistung",
                        "Keine Kollisionen durch geordnete Datenübertragung",
                        "Einfache Protokolle möglich",
                        "Vorhersagbare Übertragungszeiten",
                    ],
                    disadvantages: [
                        "Ausfall eines Geräts kann das gesamte Netzwerk lahmlegen",
                        "Schwierige Rekonfiguration",
                        "Langsamere Datenübertragung bei vielen Geräten",
                        "Probleme bei der Erweiterung",
                    ],
                    usage: "Früher in Token Ring-Netzwerken, heute noch in FDDI (Fiber Distributed Data Interface) und einigen industriellen Netzwerken verwendet.",
                },
                mesh: {
                    name: "Mesh-Topologie",
                    description:
                        "In einer Mesh-Topologie ist jedes Gerät mit mehreren oder allen anderen Geräten verbunden. Es gibt vollvermaschte (jeder mit jedem) und teilvermaschte Varianten.",
                    advantages: [
                        "Hohe Ausfallsicherheit durch Redundanz",
                        "Optimale Pfadfindung möglich",
                        "Keine zentrale Abhängigkeit",
                        "Hohe Übertragungsgeschwindigkeit durch parallele Pfade",
                    ],
                    disadvantages: [
                        "Sehr hohe Kosten für Verkabelung",
                        "Komplexe Konfiguration und Verwaltung",
                        "Hoher Wartungsaufwand",
                        "Skalierungsprobleme bei vielen Geräten",
                    ],
                    usage: "Hauptsächlich in kritischen Anwendungen wie Rechenzentren, Backbone-Netzwerken und drahtlosen Mesh-Netzwerken für erweiterte Abdeckung.",
                },
                tree: {
                    name: "Baum-Topologie",
                    description:
                        "Die Baum-Topologie kombiniert mehrere Stern-Topologien in einer hierarchischen Struktur. Es gibt eine Wurzel und Äste mit Blättern (Endgeräte).",
                    advantages: [
                        "Skalierbar und erweiterbar",
                        "Hierarchische Organisation",
                        "Lokalisierte Fehlerauswirkungen",
                        "Strukturierte Verkabelung möglich",
                    ],
                    disadvantages: [
                        "Abhängigkeit von höheren Ebenen",
                        "Komplexere Konfiguration",
                        "Potentiell längere Übertragungswege",
                        "Ausfall der Wurzel betrifft große Teile",
                    ],
                    usage: "Weit verbreitet in Unternehmensnetzwerken, Campus-Netzwerken und strukturierter Verkabelung in Gebäuden mit Verteilern auf verschiedenen Ebenen.",
                },
                hybrid: {
                    name: "Hybrid-Topologie",
                    description:
                        "Eine Hybrid-Topologie kombiniert zwei oder mehr verschiedene Topologien zu einem Netzwerk. Verschiedene Bereiche können unterschiedliche Topologien verwenden.",
                    advantages: [
                        "Flexibilität in der Netzwerkgestaltung",
                        "Optimierung für verschiedene Anforderungen",
                        "Skalierbarkeit durch modularen Aufbau",
                        "Kostenoptimierung durch angepasste Lösungen",
                    ],
                    disadvantages: [
                        "Komplexe Planung und Design erforderlich",
                        "Schwierigere Fehlerbehebung",
                        "Verschiedene Verwaltungstools nötig",
                        "Potentielle Kompatibilitätsprobleme",
                    ],
                    usage: "Standard in großen Unternehmensnetzwerken, Internet-Infrastruktur und modernen Campus-Netzwerken, wo verschiedene Bereiche unterschiedliche Anforderungen haben.",
                },
            },
            responsiveOptions: [
                {
                    breakpoint: "1400px",
                    numVisible: 5,
                    numScroll: 1,
                },
                {
                    breakpoint: "1100px",
                    numVisible: 4,
                    numScroll: 1,
                },
                {
                    breakpoint: "900px",
                    numVisible: 3,
                    numScroll: 1,
                },
                {
                    breakpoint: "650px",
                    numVisible: 2,
                    numScroll: 1,
                },
                {
                    breakpoint: "400px",
                    numVisible: 1,
                    numScroll: 1,
                },
            ],
        };
    },
    computed: {
        computedNumVisible() {
            return Math.min(this.currentNumVisible, this.topologies.length);
        },
        shouldBeCircular() {
            return this.computedNumVisible < this.topologies.length;
        },
        shouldShowNavigators() {
            return this.computedNumVisible < this.topologies.length;
        }
    },
    mounted() {
        this.updateNumVisible();
        window.addEventListener('resize', this.updateNumVisible);
    },
    beforeUnmount() {
        window.removeEventListener('resize', this.updateNumVisible);
    },
    methods: {
        updateNumVisible() {
            const width = window.innerWidth;
            if (width > 1400) {
                this.currentNumVisible = 6;
            } else if (width > 1100) {
                this.currentNumVisible = 5;
            } else if (width > 900) {
                this.currentNumVisible = 4;
            } else if (width > 650) {
                this.currentNumVisible = 3;
            } else if (width > 400) {
                this.currentNumVisible = 2;
            } else {
                this.currentNumVisible = 1;
            }
        },
        selectTopology(topologyKey) {
            this.selectedTopology = topologyKey;
        },
        navigateToPcapTable() {
            // Map topology keys to PCAP demo names
            const topologyToPcapMap = {
                'mesh': 'Mesh Demo',
                'ring': 'Ring Demo', 
                'star': 'Star Demo',
                'tree': 'Tree Demo'
            };
            
            const pcapName = topologyToPcapMap[this.selectedTopology];
            if (pcapName) {
                this.$router.push({
                    path: '/pcap-table',
                    query: { topology: pcapName }
                });
            } else {
                // For topologies without demo data, just navigate to the table
                this.$router.push('/pcap-table');
            }
        }
    },
};
</script>

<style scoped>
:global(html, body) {
    overflow-y: auto !important;
    height: auto !important;
    min-height: 100vh;
}

.topology-card {
    padding: 1rem;
    max-width: 100%;
    margin: 0 auto;
    box-sizing: border-box;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
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

.carousel {
    margin: 1rem 0;
    padding: 0.5rem;
    width: 100%;
    box-sizing: border-box;
    flex-shrink: 0;
}

.topology-item {
    background: var(--nlb-bg-primary);
    border-radius: 12px;
    padding: 1rem;
    margin: 0 0.25rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
    cursor: pointer;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.6rem;
    height: 200px;
    width: 100%;
    min-width: 150px;
    max-width: 200px;
    box-sizing: border-box;
}

.topology-item:hover {
    transform: translateY(-5px);
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}

.topology-item.selected {
    border: 2px solid var(--nlb-accent);
    box-shadow: 0 6px 12px rgba(0, 122, 217, 0.2);
}

.topology-icon {
    font-size: 2.2rem;
    background: var(--nlb-gradient-accent);
    width: 60px;
    height: 60px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--nlb-text-light);
    margin-bottom: 0.5rem;
}

.topology-name {
    font-size: 1.1rem;
    font-weight: bold;
    color: var(--nlb-text-primary);
    text-align: center;
    margin-bottom: 0.3rem;
}

.topology-brief {
    color: var(--nlb-text-secondary);
    text-align: center;
    font-size: 0.9rem;
    line-height: 1.4;
    margin-bottom: 1rem;
    flex-grow: 1;
}

.p-button-primary {
    background: var(--nlb-primary);
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    color: var(--nlb-text-light);
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    transition: all 0.3s ease;
    font-size: 1rem;
    white-space: nowrap;
    margin-top: 1rem;
}

.p-button-primary:hover {
    background: var(--nlb-primary-dark);
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.topology-details {
    background: var(--nlb-bg-muted);
    border-radius: 8px;
    padding: 1rem;
    margin-top: 1rem;
    border-left: 4px solid var(--nlb-info);
    max-width: 100%;
    box-sizing: border-box;
    overflow-wrap: break-word;
    flex-grow: 1;
}

.topology-details.active {
    animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.details-title {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--nlb-text-primary);
    margin-bottom: 1rem;
}

.details-section {
    margin-bottom: 1rem;
}

.details-section h4 {
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--nlb-text-secondary);
    margin-bottom: 0.5rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.details-section p {
    font-size: 0.875rem;
    color: var(--nlb-text-muted);
    line-height: 1.6;
}

.advantages-list,
.disadvantages-list {
    list-style: none;
    font-size: 0.875rem;
    padding-left: 0;
}

.advantages-list li {
    color: var(--nlb-success);
    margin-bottom: 0.25rem;
    position: relative;
    padding-left: 1.25rem;
    line-height: 1.5;
}

.advantages-list li::before {
    content: "✓";
    position: absolute;
    left: 0;
    font-weight: bold;
}

.disadvantages-list li {
    color: var(--nlb-error);
    margin-bottom: 0.25rem;
    position: relative;
    padding-left: 1.25rem;
    line-height: 1.5;
}

.disadvantages-list li::before {
    content: "✗";
    position: absolute;
    left: 0;
    font-weight: bold;
}

.prompt-text {
    text-align: center;
    color: var(--nlb-text-muted);
    font-size: 0.875rem;
    font-style: italic;
    margin-top: 2rem;
    padding: 1rem;
}

:deep(.p-carousel) {
    background: transparent;
    width: 100%;
    max-width: 100%;
    overflow: visible;
}

:deep(.p-carousel-content) {
    display: flex;
    align-items: center;
    width: 100%;
    overflow: visible;
}

:deep(.p-carousel-container) {
    display: flex;
    align-items: center;
    width: 100%;
    overflow: hidden;
}

:deep(.p-carousel-items-content) {
    overflow: hidden;
    width: 100%;
}

:deep(.p-carousel-item) {
    display: flex;
    justify-content: center;
    padding: 0 0.25rem;
    flex: 0 0 auto;
    box-sizing: border-box;
}

:deep(.p-carousel-prev),
:deep(.p-carousel-next) {
    background: #4f46e5;
    color: white;
    border: none;
    border-radius: 50%;
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 0.5rem;
    flex-shrink: 0;
}

:deep(.p-carousel-prev:hover),
:deep(.p-carousel-next:hover) {
    background: #4338ca;
}

@media (max-width: 768px) {
    .topology-card {
        padding: 0.5rem;
    }
    
    .header-section {
        margin-bottom: 1rem;
    }
    
    .page-title {
        font-size: 1.5rem;
    }
    
    .page-description {
        font-size: 1rem;
    }
    
    .topology-item {
        margin: 0 0.125rem;
        padding: 0.75rem;
        height: 180px;
        min-width: 140px;
        max-width: 180px;
    }
    
    .topology-icon {
        width: 50px;
        height: 50px;
        font-size: 1.8rem;
    }
    
    .topology-name {
        font-size: 1rem;
    }
    
    .topology-brief {
        font-size: 0.8rem;
    }
    
    .carousel {
        padding: 0.25rem;
        margin: 0.5rem 0;
    }
    
    .topology-details {
        padding: 0.75rem;
        margin-top: 0.5rem;
    }
    
    :deep(.p-carousel-prev),
    :deep(.p-carousel-next) {
        width: 28px;
        height: 28px;
        margin: 0 0.25rem;
    }
}
</style>