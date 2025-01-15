<template>
   <section class="px-4">
      <h1 class="text-base uppercase font-medium py-4">Image to process</h1>
      <Separator />

      <InputImagesZone />
   </section>

   <section class="px-4">
      <h1 class="text-base uppercase font-medium py-4">History</h1>
      <div class="shrink-0 bg-border relative h-px w-full"></div>
      <div class="py-12 rounded-lg border border-2 border-dashed my-4"></div>
   </section>
</template>

<script setup lang="ts">
   import { Separator } from '@/components/ui/separator';
   import InputImagesZone from '@/components/InputImagesZone.vue';
</script>
