<template>
    <div class="card">
        <h1>Netzwerk-Topologien</h1>
        <h3>Wähle eine dieser Topologien, um sie zu simulieren.</h3>
        <Carousel
            :value="texts"
            :numVisible="2"
            :numScroll="1"
            :responsiveOptions="responsiveOptions"
            circular="true"
            class="carousel"
        >
            <template #item="{ data, index }">
                <div v-if="index === 0" class="card carousel-content">
                    <VueFlowGraph />
                </div>
                <div v-if="index === 1" class="card carousel-content">
                    <NetworkGraph />
                </div>
                <div v-if="index === 2" class="card carousel-content">
                    <h1>Terminal</h1>
                    <!-- <EmbededTerminal /> -->
                </div>
                <div v-else class="card carousel-content">
                    <i :class="data.icon" class="carousel-icon"></i>
                    <p class="carousel-text">{{ data.text }}</p>
                    <!-- <Button asChild v-slot="slotProps">
                        <RouterLink to="/" :class="slotProps.class"
                            >Router</RouterLink
                        >
                    </Button> -->
                </div>
            </template>
        </Carousel> 
    </div>
</template>

<script>
import Carousel from "primevue/carousel";

import VueFlowGraph from "./VueFlowGraph.vue";
import NetworkGraph from "./NetworkGraph.vue";
import Button from "primevue/button";
import EmbededTerminal from "./EmbededTerminal.vue";
import CarouselGraphs from "./CarouselGraphs.vue";

export default {
    name: "CarouselGraphs",
    components: {
        Carousel,
        VueFlowGraph,
        NetworkGraph,
        EmbededTerminal,
        Button,
    },
    data() {
        return {
            texts: [
                {
                    text: "Slide 1: Welcome to our platform!",
                    icon: "pi pi-home",
                },
                {
                    text: "Slide 2: Explore our features.",
                    icon: "pi pi-search",
                },
                {
                    text: "Slide 3: Contact us for more info.",
                    icon: "pi pi-envelope",
                },
            ],
            responsiveOptions: [
                {
                    breakpoint: "1201px",
                    numVisible: 2,
                    numScroll: 1,
                },
                {
                    breakpoint: "1200px",
                    numVisible: 1,
                    numScroll: 1,
                },
            ],
        };
    },
};
</script>

<style scoped>
.card {
    flex-direction: column;
}

.carousel {
    display: flex;
    flex-direction: column;
    height: auto;
    height: 100%;
    min-height: auto;
    padding: 1vh 0;
    overflow: visible;
    align-items: center;
    justify-content: center;
    height: auto;
    height: 100%;
    text-align: center;
    padding: 20px;
    padding-bottom: 0;
    overflow: visible;
    flex-grow: 1;
}

.carousel-content {
    display: flex;
    flex-direction: column;
    padding: 20px;
    /* background: wheat; */
    align-items: center;
    justify-content: center;
    height: auto;
    text-align: center;
    overflow: visible;
}

.carousel-icon {
    font-size: 2rem;
    margin-bottom: 10px;
    color: #007ad9;
}

.carousel-text {
    font-size: 1.2rem;
    color: #333;
}
</style>
