<template>
   <div
      class="max-w-[1320px] m-auto border-x border-dashed grid lg:grid-cols-3 lg:grid-rows-2 relative"
   >
      <section class="px-4 lg:col-span-2">
         <h1 class="text-base uppercase font-medium py-4">Image to process</h1>
         <Separator />

         <ImportZone
            @imported="handleImported"
            :scale-factor="scaleFactor"
         />
      </section>

      <section
         id="operations-zone"
         class="lg:row-start-1 lg:row-span-2 lg:col-start-3"
         ref="operationsZone"
      >
         <OperationsZone
            :image-to-process="imageToProcess"
            :class="'fixed'"
            :style="fixedStyle"
            @change-scale-factor="handleChangeScaleFactor"
         />
      </section>

      <section class="px-4 lg:col-start-1 lg:col-span-2 lg:row-start-2">
         <h1 class="text-base uppercase font-medium py-4">History</h1>
         <div class="shrink-0 bg-border relative h-px w-full"></div>
         <div class="py-12 rounded-lg border border-2 border-dashed my-4"></div>
      </section>
   </div>
</template>

<script setup lang="ts">
   import { Separator } from '@/components/ui/separator';
   import ImportZone from '@/components/ImportZone.vue';
   import OperationsZone from '@/components/OperationsZone.vue';
   import type { Image } from '@/utils/types';
   import { ref, reactive, onMounted, onBeforeUnmount } from 'vue';
   import { useWindowSize } from '@vueuse/core';

   const imageToProcess = ref<Image | null>(null);
   const handleImported = (image: Image) => {
      imageToProcess.value = image;
   };
   const scaleFactor = ref<number>(2);
   const handleChangeScaleFactor = (scale: number) => {
      scaleFactor.value = scale;
   };

   const operationsZone = ref<HTMLElement | null>(null);
   const { width, height } = useWindowSize();
   const fixedStyle = reactive({
      left: '0px',
      width: '0px',
   });

   const updateFixedPosition = () => {
      if (operationsZone.value && width.value >= 1024) {
         const rect = operationsZone.value.getBoundingClientRect();
         fixedStyle.left = rect.left + 'px';
         fixedStyle.width = rect.width + 'px';
      }
   };

   onMounted(() => {
      if (width.value >= 1024) {
         updateFixedPosition();
      }
      window.addEventListener('resize', updateFixedPosition);
   });

   onBeforeUnmount(() => {
      if (width.value >= 1024) {
         updateFixedPosition();
      }
      window.removeEventListener('resize', updateFixedPosition);
   });
</script>
