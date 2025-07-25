import { createRouter, createWebHistory } from "vue-router";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "start",
      component: () => import("@/views/StartPage.vue"),
    },
    {
      path: "/controller",
      name: "home",
      component: () => import("@/views/HomeView.vue"),
    },
    {
      path: "/create-topology",
      name: "create-topology",
      component: () => import("@/views/CreateTopologyView.vue"),
    },
    {
      path: "/topologies",
      name: "topologies",
      component: () => import("@/views/TopologiesView.vue"),
    },
    // {
    //   path: "/lab",
    //   name: "lab",
    //   component: () => import("@/views/LabView.vue"),
    // },
    {
      path: "/graph",
      name: "graph",
      component: () => import("@/views/GraphView.vue"),
    },
    {
      path: "/pcap-table",
      name: "pcap-table",
      component: () => import("@/views/PcapTableView.vue"),
    },
    {
      path: "/saved-pcaps",
      name: "saved-pcaps",
      component: () => import("@/views/SavedPcapsView.vue"),
    },
  ],
});

export default router;
