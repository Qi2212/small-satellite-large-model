import { createApp } from 'vue'
import pinia from "@/stores/index"
import "element-plus/dist/index.css";
import "./assets/main.scss";
import "./main.css"
import "/src/assets/iconfont.js";

import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(pinia)
app.use(router)

app.mount('#app')
