import { createApp } from "vue";
import { createRouter, createWebHistory } from "vue-router";
import App from "./App.vue";
import OperadorasList from "./views/OperadorasList.vue";
import OperadoraDetail from "./views/OperadoraDetail.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", component: OperadorasList },
    { path: "/operadora/:cnpj", component: OperadoraDetail },
  ],
});

createApp(App).use(router).mount("#app");
