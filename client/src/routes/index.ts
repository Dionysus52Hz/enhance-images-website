import { createRouter, createWebHistory } from 'vue-router';
import EnhancerView from '@/views/EnhancerView.vue';
import FiltersView from '@/views/FiltersView.vue';
import ResultView from '@/views/ResultView.vue';

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
   {
      path: '/result/:model/:scale',
      component: ResultView,
      name: 'results-view',
   },
];

const router = createRouter({
   history: createWebHistory(),
   routes,
});

export default router;
