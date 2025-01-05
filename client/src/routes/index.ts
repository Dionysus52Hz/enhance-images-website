import { createRouter, createWebHistory } from 'vue-router';
import EnhancerView from '@/views/EnhancerView.vue';
import FiltersView from '@/views/FiltersView.vue';

const routes = [
   {
      path: '/',
      component: EnhancerView,
      name: 'enhancer-view',
   },
   {
      path: '/filters',
      component: FiltersView,
      name: 'filters-view',
   },
];

const router = createRouter({
   history: createWebHistory(),
   routes,
});

export default router;
