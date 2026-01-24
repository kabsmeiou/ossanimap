import { createRouter, createWebHistory } from 'vue-router'

import Index from './Index.vue'
import Pack from './Pack.vue'

const routes = [
    {path: '/', component: Index},
    {path: '/pack/:packId', name: 'PackDetail', component: Pack}
]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

export default router;