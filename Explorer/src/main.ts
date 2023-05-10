import { createApp } from 'vue'
import App from './App.vue'

import ElementPlus from 'element-plus'
import VueCodemirror from 'vue-codemirror'
import 'element-plus/theme-chalk/index.css'
import './dark.css'

createApp(App).use(ElementPlus).use(VueCodemirror).mount('#app')
