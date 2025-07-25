import "./assets/main.css";
import "./assets/index.css";
import "primeicons/primeicons.css";

import { createApp } from "vue";
import PrimeVue from "primevue/config";
import Aura from "@primeuix/themes/aura";
import App from "./App.vue";
import Ripple from "primevue/ripple";

import axios from "axios";
import store from "./store";
import router from "./router";

import DataTable from "primevue/datatable";
import Column from "primevue/column";
import ToastService from "primevue/toastservice";
import ConfirmationService from "primevue/confirmationservice";

// Create Axios instance with base configuration
const apiClient = axios.create({
  baseURL: "http://localhost:5050/api", // Flask backend
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
  },
});

const app = createApp(App);
app.use(router);
app.use(ToastService);
app.use(ConfirmationService);
app.use(store);

// Add Axios to Vue prototype and provide for Composition API
app.config.globalProperties.$axios = apiClient;
app.provide("axios", apiClient);

// PrimeVue setup
app.use(PrimeVue, {
  theme: {
    preset: Aura,
    options: {
      darkModeSelector: 'none',
    }
  },
});
app.directive("ripple", Ripple);

// Register components
app.component("DataTable", DataTable);
app.component("Column", Column);

app.mount("#app");
