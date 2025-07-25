<template>
    <div class="homepage">
        <section class="hero-section">
            <div class="hero-content">
                <div class="hero-text">
                    <h1 class="hero-title">Willkommen bei NetLab</h1>
                    <p class="hero-subtitle">
                        Ihr virtuelles Netzwerklabor für praktisches Lernen und
                        Experimentieren
                    </p>
                    <p class="hero-description">
                        Entdecken Sie verschiedene Netzwerktopologien, erstellen
                        Sie eigene Konfigurationen und analysieren Sie
                        Netzwerkverkehr in einer sicheren, virtuellen Umgebung.
                    </p>
                    <div class="hero-buttons">
                        <button class="btn btn-primary" @click="navigateTo('controller')">
                            <i class="pi pi-play"></i>
                            Jetzt starten
                        </button>
                        <button
                            class="btn btn-secondary"
                            @click="scrollToFeatures"
                        >
                            <i class="pi pi-info-circle"></i>
                            Mehr erfahren
                        </button>
                    </div>
                </div>
                <div class="hero-visual">
                    <div class="network-animation">
                        <div class="node central-node">
                            <i class="pi pi-server"></i>
                        </div>
                        <div class="node satellite-node node-1">
                            <i class="pi pi-desktop"></i>
                        </div>
                        <div class="node satellite-node node-2">
                            <i class="pi pi-mobile"></i>
                        </div>
                        <div class="node satellite-node node-3">
                            <i class="pi pi-tablet"></i>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Features Section -->
        <section class="features-section" id="features">
            <div class="container">
                <h2 class="section-title">Funktionen und Möglichkeiten</h2>
                <div class="features-grid">
                    <div
                        class="feature-card"
                        @click="navigateTo('controller')"
                        :class="{ 'card-hover': hoveredCard === 'controller' }"
                        @mouseenter="hoveredCard = 'controller'"
                        @mouseleave="hoveredCard = null"
                    >
                        <div class="feature-icon">
                            <i class="pi pi-cog"></i>
                        </div>
                        <h3>Netzwerk-Controller</h3>
                        <p>
                            Steuern und verwalten Sie Ihre Netzwerkgeräte
                            zentral. Konfigurieren Sie Knoten in Echtzeit.
                        </p>
                        <div class="feature-arrow">
                            <i class="pi pi-arrow-right"></i>
                        </div>
                    </div>
                    <div
                        class="feature-card"
                        @click="navigateTo('topologies')"
                        :class="{ 'card-hover': hoveredCard === 'topologies' }"
                        @mouseenter="hoveredCard = 'topologies'"
                        @mouseleave="hoveredCard = null"
                    >
                        <div class="feature-icon">
                            <i class="pi pi-sitemap"></i>
                        </div>
                        <h3>Netzwerk-Topologien</h3>
                        <p>
                            Entdecken Sie verschiedene Netzwerkstrukturen wie
                            Ring-, Stern-, Bus- und Mesh-Topologien. Lernen Sie
                            die Vor- und Nachteile jeder Topologie kennen.
                        </p>
                        <div class="feature-arrow">
                            <i class="pi pi-arrow-right"></i>
                        </div>
                    </div>

                    <div
                        class="feature-card"
                        @click="navigateTo('graph')"
                        :class="{ 'card-hover': hoveredCard === 'graph' }"
                        @mouseenter="hoveredCard = 'graph'"
                        @mouseleave="hoveredCard = null"
                    >
                        <div class="feature-icon">
                            <i class="pi pi-chart-bar"></i>
                        </div>
                        <h3>Graph-Visualisierung</h3>
                        <p>
                            Visualisieren Sie Netzwerktopologien als
                            interaktiven Graphen. Analysieren Sie Verbindungen,
                            Knotenpunkte und Datenflüsse.
                        </p>
                        <div class="feature-arrow">
                            <i class="pi pi-arrow-right"></i>
                        </div>
                    </div>

                    <div
                        class="feature-card"
                        @click="navigateTo('pcap-table')"
                        :class="{ 'card-hover': hoveredCard === 'pcap-table' }"
                        @mouseenter="hoveredCard = 'pcap-table'"
                        @mouseleave="hoveredCard = null"
                    >
                        <div class="feature-icon">
                            <i class="pi pi-table"></i>
                        </div>
                        <h3>Paket-Analyse</h3>
                        <p>
                            Analysieren Sie die aufgezeichneten Netzwerkpakete
                            in einer detaillierten Tabelle. Untersuchen Sie
                            Protokolle, Timing und Datenflüsse.
                        </p>
                        <div class="feature-arrow">
                            <i class="pi pi-arrow-right"></i>
                        </div>
                    </div>
                    <div
                        class="feature-card"
                        @click="navigateTo('create-topology')"
                        :class="{ 'card-hover': hoveredCard === 'create' }"
                        @mouseenter="hoveredCard = 'create'"
                        @mouseleave="hoveredCard = null"
                    >
                        <div class="feature-icon">
                            <i class="pi pi-plus-circle"></i>
                        </div>
                        <h3>Topologie erstellen</h3>
                        <p>
                            In Arbeit...
                            Erstellen Sie eigene Netzwerktopologien nach Ihren
                            Anforderungen.
                        </p>
                        <div class="feature-arrow">
                            <i class="pi pi-arrow-right"></i>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Quick Start Section -->
        <section class="quickstart-section">
            <div class="container">
                <h2 class="section-title">Schnellstart</h2>
                <div class="quickstart-steps">
                    <div
                        class="step"
                        v-for="(step, index) in quickstartSteps"
                        :key="index"
                    >
                        <div class="step-number">{{ index + 1 }}</div>
                        <div class="step-content">
                            <h3>{{ step.title }}</h3>
                            <p>{{ step.description }}</p>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Stats Section -->
        <section class="stats-section">
            <div class="container">
                <div class="stats-grid">
                    <div class="stat-item">
                        <div class="stat-number">4</div>
                        <div class="stat-label">Netzwerk-Topologien</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">∞</div>
                        <div class="stat-label">Eigene Konfigurationen</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">100%</div>
                        <div class="stat-label">Virtuell & Sicher</div>
                    </div>
                </div>
            </div>
        </section>
    </div>
</template>

<script>
export default {
    name: "NetLabHomepage",
    data() {
        return {
            hoveredCard: null,
            quickstartSteps: [
                {
                    title: "Topologie auswählen",
                    description:
                        "Wählen Sie eine der verfügbaren Netzwerktopologien aus oder erstellen Sie eine eigene",
                },
                {
                    title: "Knoten konfigurieren",
                    description:
                        "Konfigurieren Sie die Netzwerkknoten nach Ihren Anforderungen",
                },
                {
                    title: "Simulation starten",
                    description: "Beobachten Sie das Netzwerkverhalten",
                },
                {
                    title: "Analysieren & Lernen",
                    description:
                        "Analysieren Sie die Ergebnisse und erweitern Sie Ihr Netzwerkwissen",
                },
            ],
        };
    },
    methods: {
        navigateTo(section) {
            this.$router.push(`/${section}`);
        },
        scrollToFeatures() {
            document.getElementById("features").scrollIntoView({
                behavior: "smooth",
            });
        },
    },
};
</script>

<style scoped>
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

.homepage {
    min-height: 100vh;
    background: var(--nlb-gradient-primary);
    font-family:
        -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

/* Navigation */
.navbar {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    padding: 1rem 0;
    position: sticky;
    top: 0;
    z-index: 100;
    box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
}

.nav-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.brand-title {
    color: var(--nlb-primary);
    font-size: 1.5rem;
    font-weight: bold;
}

.nav-links {
    display: flex;
    gap: 2rem;
}

.nav-link {
    color: var(--nlb-text-primary);
    text-decoration: none;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    transition: all 0.3s ease;
}

.nav-link:hover {
    background: var(--nlb-primary);
    color: var(--nlb-text-light);
    transform: translateY(-2px);
}

.user-info {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: var(--nlb-text-secondary);
    font-size: 0.9rem;
}

/* Hero Section */
.hero-section {
    padding: 6rem 2rem;
    max-width: 1200px;
    margin: 0 auto;
}

.hero-content {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 4rem;
    align-items: center;
}

.hero-title {
    font-size: 3.5rem;
    font-weight: bold;
    color: var(--nlb-text-light);
    margin-bottom: 1rem;
    line-height: 1.2;
}

.hero-subtitle {
    font-size: 1.25rem;
    color: rgba(255, 255, 255, 0.9);
    margin-bottom: 1.5rem;
}

.hero-description {
    color: rgba(255, 255, 255, 0.8);
    line-height: 1.6;
    margin-bottom: 2rem;
}

.hero-buttons {
    display: flex;
    gap: 1rem;
}

.btn {
    padding: 1rem 2rem;
    border: none;
    border-radius: 12px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    transition: all 0.3s ease;
}

.btn-primary {
    background: var(--nlb-bg-primary);
    color: var(--nlb-primary);
}

.btn-primary:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
}

.btn-secondary {
    background: rgba(255, 255, 255, 0.2);
    color: var(--nlb-text-light);
    border: 2px solid rgba(255, 255, 255, 0.3);
}

.btn-secondary:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: translateY(-3px);
}

/* Network Animation */
.hero-visual {
    display: flex;
    justify-content: center;
    align-items: center;
}

.network-animation {
    position: relative;
    width: 300px;
    height: 300px;
}

.node {
    position: absolute;
    width: 60px;
    height: 60px;
    background: rgba(255, 255, 255, 0.95);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    color: var(--nlb-primary);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    z-index: 10;
    cursor: pointer;
}

.node:hover {
    background: var(--nlb-bg-primary);
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.2);
}

.central-node {
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 80px;
    height: 80px;
    font-size: 2rem;
}

.central-node:hover {
    background: var(--nlb-bg-primary);
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.2);
}

.node-1 {
    top: 15%;
    left: 50%;
    transform: translate(-50%, -50%);
}

.node-2 {
    top: 75%;
    left: 15%;
    transform: translate(-50%, -50%);
}

.node-3 {
    top: 75%;
    left: 85%;
    transform: translate(-50%, -50%);
}

/* Features Section */
.features-section {
    background: white;
    padding: 6rem 0;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 2rem;
}

.section-title {
    text-align: center;
    font-size: 2.5rem;
    color: var(--nlb-text-primary);
    margin-bottom: 3rem;
    font-weight: bold;
}

.features-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 2rem;
}

.feature-card {
    background: var(--nlb-bg-primary);
    padding: 2rem;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    cursor: pointer;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.feature-card:hover,
.card-hover {
    transform: translateY(-8px);
    box-shadow: 0 20px 40px rgba(79, 70, 229, 0.15);
}

.feature-icon {
    width: 60px;
    height: 60px;
    background: var(--nlb-gradient-accent);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 1.5rem;
}

.feature-icon i {
    font-size: 1.5rem;
    color: var(--nlb-text-light);
}

.feature-card h3 {
    color: var(--nlb-text-primary);
    font-size: 1.25rem;
    font-weight: bold;
    margin-bottom: 1rem;
}

.feature-card p {
    color: var(--nlb-text-secondary);
    line-height: 1.6;
    margin-bottom: 1.5rem;
}

.feature-arrow {
    position: absolute;
    top: 2rem;
    right: 2rem;
    color: var(--nlb-primary);
    opacity: 0;
    transition: all 0.3s ease;
}

.feature-card:hover .feature-arrow,
.card-hover .feature-arrow {
    opacity: 1;
    transform: translateX(5px);
}

/* Quick Start Section */
.quickstart-section {
    background: var(--nlb-bg-secondary);
    padding: 6rem 0;
}

.quickstart-steps {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 2rem;
}

.step {
    display: flex;
    align-items: flex-start;
    gap: 1rem;
}

.step-number {
    width: 40px;
    height: 40px;
    background: var(--nlb-primary);
    color: var(--nlb-text-light);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    flex-shrink: 0;
}

.step-content h3 {
    color: var(--nlb-text-primary);
    font-size: 1.1rem;
    font-weight: bold;
    margin-bottom: 0.5rem;
}

.step-content p {
    color: var(--nlb-text-secondary);
    line-height: 1.6;
}

/* Stats Section */
.stats-section {
    background: linear-gradient(135deg, var(--nlb-text-primary), var(--nlb-text-secondary));
    padding: 4rem 0;
    color: var(--nlb-text-light);
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 2rem;
    text-align: center;
}

.stat-number {
    font-size: 2.5rem;
    font-weight: bold;
    margin-bottom: 0.5rem;
    color: var(--nlb-text-light);
}

.stat-label {
    color: rgba(255, 255, 255, 0.7);
    font-size: 1rem;
}

/* Responsive Design */
@media (max-width: 768px) {
    .hero-content {
        grid-template-columns: 1fr;
        text-align: center;
    }

    .hero-title {
        font-size: 2.5rem;
    }

    .nav-links {
        display: none;
    }

    .features-grid {
        grid-template-columns: 1fr;
    }

    .hero-buttons {
        justify-content: center;
    }
}
</style>
