<script setup>
import MenuBar from "./components/MenuBar.vue";
import Toast from "primevue/toast";

import { useRouter } from "vue-router";

const router = useRouter();
</script>

<template>
    <div id="app">
        <header>
            <MenuBar />
        </header>
        <Toast />
        <RouterView />
    </div>
</template>
