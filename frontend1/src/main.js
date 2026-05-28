import { createApp } from 'vue';
import { createPinia } from 'pinia';
import { router } from './router';
import './styles/main.css';
import App from './App.vue';

// 1. createApp(App): Crea la aplicación Vue principal
// 2. use(createPinia()): Agrega el estado global (datos de la app)
// 3. use(router): Agrega el sistema de rutas (navegación)
// 4. mount('#app'): Conecta todo esto al index.html
createApp(App).use(createPinia()).use(router).mount('#app');
