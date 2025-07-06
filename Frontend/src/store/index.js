import { createStore } from "vuex";

export default createStore({
  state() {
    return {
      user: {
        id: localStorage.getItem("userId") || null,
      },
    };
  },
  mutations: {
    setUser(state, user) {
      state.user = user;
      // Persist to localStorage
      if (user?.id) {
        localStorage.setItem("userId", user.id);
      } else {
        localStorage.removeItem("userId");
      }
    },
    initializeUser(state) {
      // Generate guest ID if none exists
      if (!state.user.id) {
        const guestId = "guest_" + Math.random().toString(36).substring(2, 8);
        state.user.id = guestId;
        localStorage.setItem("userId", guestId);
      }
    },
  },
  actions: {
    initializeUser({ commit }) {
      commit("initializeUser");
    },
  },
  getters: {
    userId: (state) => state.user.id,
    isGuest: (state) => !state.user.id || state.user.id.startsWith("guest_"),
  },
});
