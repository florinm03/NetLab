<template>
    <div>
        <Menubar :model="items">
            <template #start>
                <RouterLink to="/" class="logo-link">
                    <h2 class="logo">NetLab</h2>
                </RouterLink>
            </template>
            <template #item="{ item, props }">
                <RouterLink
                    v-if="item.route"
                    v-slot="{ href, navigate, isActive }"
                    :to="item.route"
                    custom
                >
                    <a
                        :href="href"
                        v-bind="props.action"
                        @click="navigate"
                        :class="{ 'active-link': isActive }"
                    >
                        <span v-if="item.icon">
                            <i :class="item.icon"></i>
                        </span>
                        <span>{{ item.label }}</span>
                    </a>
                </RouterLink>
                <a v-else v-bind="props.action">
                    <span v-if="item.icon">
                        <i :class="item.icon"></i>
                    </span>
                    <span>{{ item.label }}</span>
                </a>
            </template>
            <template #end>
                                    <div class="user-info-sub">
                        <div
                            class="user-info"
                            :class="{ 
                                'easter-egg-active': easterEggActive,
                                'click-progress': clickCount > 0 && clickCount < 5
                            }"
                        >
                        <i
                            :class="userIconClass"
                            @click="triggerEasterEgg"
                            class="user-icon"
                            :style="{
                                transform: easterEggActive
                                    ? 'rotate(360deg) scale(1.2)'
                                    : clickCount > 0 && clickCount < 5
                                    ? `scale(${1 + clickCount * 0.05})`
                                    : '',
                                opacity: clickCount > 0 && clickCount < 5 ? 0.7 + clickCount * 0.06 : 1,
                            }"
                        ></i>
                        <span 
                            @click="handleMessageClick"
                            :class="{ 'message-clicked': messageClicked }"
                            class="easter-egg-message"
                        >{{ easterEggMessage }}</span>
                    </div>

                    <div v-if="showConfetti" class="confetti-container">
                        <div
                            v-for="i in 20"
                            :key="i"
                            class="confetti"
                            :style="confettiStyle(i)"
                        ></div>
                    </div>
                </div>
            </template>
        </Menubar>
    </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { RouterLink } from "vue-router";
import Menubar from "primevue/menubar";
import Avatar from "primevue/avatar";
import { useStore } from "vuex";

const store = useStore();

const items = ref([
    {
        label: "Home",
        icon: "pi pi-home",
        route: "/",
    },
    {
        label: "Controller",
        icon: "pi pi-cog",
        route: "/controller",
    },
    {
        label: "Topologien",
        icon: "pi pi-sitemap",
        route: "/topologies",
    },
    {
        label: "Graph",
        icon: "pi pi-chart-bar",
        route: "/graph",
    },
    {
        label: "Paket-Tabelle",
        icon: "pi pi-table",
        route: "/pcap-table",
    },
    {
        label: "Gespeicherte PCAPs",
        icon: "pi pi-database",
        route: "/saved-pcaps",
    },
    {
        label: "Erstellen",
        icon: "pi pi-plus",
        route: "/create-topology",
        class: "ml-auto-item",
    },
]);

const userId = store.state.user.id;

const easterEggActive = ref(false);
const showConfetti = ref(false);
const clickCount = ref(0);
const lastClickTime = ref(0);
const clickTimeout = ref(null);
const messageClicked = ref(false);
const currentMessage = ref("");

const easterEggMessages = [
    "You found me!",
    "NetLab Ninja detected!",
    "Secret mode activated!",
    "Nice click skills!",
    "You're awesome!",
    "Easter egg hunter!",
    "Hidden gem unlocked!",
    "Creative explorer!",
];

const easterEggIcons = [
    "pi pi-star",
    "pi pi-heart",
    "pi pi-thumbs-up",
    "pi pi-crown",
    "pi pi-bolt",
    "pi pi-diamond",
    "pi pi-gift",
];

const easterEggMessage = computed(() => {
    if (easterEggActive.value) {
        return currentMessage.value;
    }
    return `User ID: ${userId}`;
});

const userIconClass = computed(() => {
    if (easterEggActive.value) {
        const iconIndex = clickCount.value % easterEggIcons.length;
        return easterEggIcons[iconIndex];
    }
    return "pi pi-user";
});

const triggerEasterEgg = () => {
    const currentTime = Date.now();
    
    if (currentTime - lastClickTime.value > 2000) {
        clickCount.value = 0;
    }
    
    clickCount.value++;
    lastClickTime.value = currentTime;
    
    if (clickTimeout.value) {
        clearTimeout(clickTimeout.value);
    }
    
    clickTimeout.value = setTimeout(() => {
        clickCount.value = 0;
    }, 2000);
    
    if (clickCount.value >= 5) {
        easterEggActive.value = true;
        showConfetti.value = true;
        messageClicked.value = false;
        
        const randomIndex = Math.floor(Math.random() * easterEggMessages.length);
        currentMessage.value = easterEggMessages[randomIndex];
        
        clickCount.value = 0;
        
        setTimeout(() => {
            easterEggActive.value = false;
            showConfetti.value = false;
            messageClicked.value = false;
        }, 3000);
    }
};

const confettiStyle = (index) => {
    const colors = [
        "#007ad9",
        "#ff6b6b",
        "#4ecdc4",
        "#45b7d1",
        "#96ceb4",
        "#ffeaa7",
        "#dda0dd",
    ];
    const randomColor = colors[index % colors.length];
    const randomLeft = Math.random() * 100;
    const randomDelay = Math.random() * 2;
    const randomDuration = 2 + Math.random() * 2;

    return {
        backgroundColor: randomColor,
        left: `${randomLeft}%`,
        animationDelay: `${randomDelay}s`,
        animationDuration: `${randomDuration}s`,
    };
};

const handleMessageClick = () => {
    if (easterEggActive.value && !messageClicked.value) {
        messageClicked.value = true;
    }
};
</script>

<style scoped>
.user-info {
    display: flex;
    color: var(--nlb-text-primary);
    align-items: center;
    gap: 8px;
    background: rgba(250, 250, 250, 1);
    padding: 12px 16px;
    border-radius: 12px;
    backdrop-filter: blur(10px);
    transition: all 0.3s ease;
    position: relative;
}

.user-info.easter-egg-active {
    background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4);
    background-size: 400% 400%;
    animation: rainbow 2s ease infinite;
    color: white;
    box-shadow: 0 0 20px rgba(0, 122, 217, 0.5);
}

.user-info.click-progress {
    border: 2px solid rgba(0, 122, 217, 0.3);
    animation: pulse 1s ease-in-out;
}

.user-icon {
    cursor: pointer;
    transition: all 0.3s ease;
    padding: 4px;
    border-radius: 50%;
}

.user-icon:hover {
    background: rgba(0, 122, 217, 0.1);
    transform: scale(1.1);
}

.easter-egg-active .user-icon {
    animation: bounce 0.6s ease;
}

.confetti-container {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    overflow: hidden;
    border-radius: 12px;
}

.confetti {
    position: absolute;
    width: 8px;
    height: 8px;
    top: -10px;
    border-radius: 50%;
    animation: confetti-fall linear forwards;
}

@keyframes rainbow {
    0% {
        background-position: 0% 50%;
    }
    50% {
        background-position: 100% 50%;
    }
    100% {
        background-position: 0% 50%;
    }
}

@keyframes bounce {
    0%,
    20%,
    60%,
    100% {
        transform: translateY(0) rotate(0deg);
    }
    40% {
        transform: translateY(-10px) rotate(180deg);
    }
    80% {
        transform: translateY(-5px) rotate(360deg);
    }
}

@keyframes confetti-fall {
    0% {
        transform: translateY(-100px) rotate(0deg);
        opacity: 1;
    }
    100% {
        transform: translateY(200px) rotate(720deg);
        opacity: 0;
    }
}

@keyframes pulse {
    0% {
        transform: scale(1);
    }
    50% {
        transform: scale(1.02);
    }
    100% {
        transform: scale(1);
    }
}

.logo {
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2rem;
    font-weight: bold;
    color: var(--nlb-accent);
    letter-spacing: 2px;
}

.logo-link {
    text-decoration: none;
}

.logo:hover {
    color: var(--nlb-accent-dark);
    transform: scale(1.01);
}

.active-link {
    background-color: var(--nlb-info-light) !important;
    color: var(--nlb-accent) !important;
    border-radius: 6px;
    font-weight: 600;
}

.active-link i {
    color: var(--nlb-accent) !important;
}

.ml-auto-item {
    margin-left: auto;
}

.easter-egg-message {
    cursor: pointer;
    transition: color 0.3s ease;
}

.easter-egg-message.message-clicked {
    color: white !important;
}
</style>
