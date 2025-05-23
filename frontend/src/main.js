import './assets/main.css'

import { createApp } from 'vue';
import App from './App.vue';
import PrimeVue from 'primevue/config';
import Aura from '@primeuix/themes/aura';

import ToastPlugin from 'vue-toast-notification';

const app = createApp(App);

app.use(PrimeVue, {
	theme: {
        preset: Aura,
    }
}); // Install PrimeVue plugin

app.use(ToastPlugin);

app.mount('#app');
