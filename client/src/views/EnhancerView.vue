<template>
   <div
      class="max-w-[1320px] m-auto border-x border-dashed grid lg:grid-cols-3 lg:grid-rows-2"
   >
      <section class="px-4 lg:col-span-2">
         <h1 class="text-base uppercase font-medium py-4">Image to process</h1>
         <Separator />

         <InputImagesZone />
      </section>

      <section class="px-4 lg:col-start-1 lg:col-span-2 lg:row-start-2">
         <h1 class="text-base uppercase font-medium py-4">History</h1>
         <div class="shrink-0 bg-border relative h-px w-full"></div>
         <div class="py-12 rounded-lg border border-2 border-dashed my-4"></div>
      </section>

      <section
         id="operations-zone"
         class="lg:row-start-1 lg:row-span-2 lg:col-start-3"
      ></section>
   </div>
</template>

<script setup lang="ts">
   import { Separator } from '@/components/ui/separator';
   import InputImagesZone from '@/components/InputImagesZone.vue';
</script>
