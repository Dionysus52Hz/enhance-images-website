<template>
   <div
      v-if="originalImage.length > 0 && enhancedImage.length > 0"
      class="max-w-[1320px] m-auto p-4 grid lg:grid-cols-3 lg:gap-x-4 gap-y-4 border-x border-dashed"
   >
      <div class="view lg:col-span-2">
         <ImageComparison>
            <ImageComparisonHeader>
               <ImageComparisonTitle>
                  <div class="flex items-center justify-between">
                     <h3 class="">Upscale {{ scaleFactor }}x result</h3>

                     <div class="flex items-center space-x-2">
                        <Label for="switch-to-comparison-view"
                           >Comparison slider mode</Label
                        >
                        <Switch
                           id="switch-to-comparison-view"
                           @update:checked="handleChangeViewMode"
                        />
                     </div>
                  </div>
               </ImageComparisonTitle>
            </ImageComparisonHeader>

            <ImageComparisonContent
               v-if="viewMode === 'comparison'"
               :left-image="originalImage"
               :right-image="enhancedImage"
            >
            </ImageComparisonContent>

            <div v-else>
               <div class="grid grid-cols-2 gap-x-4 px-4">
                  <ImageZoomHover
                     :image="originalImage"
                     :display-mode="'pixelated'"
                     class="rounded-md outline-1 outline-offset-2 outline-dashed outline-zinc-300"
                     @height="
                        (e) => {
                           console.log(e);
                        }
                     "
                  ></ImageZoomHover>
                  <ImageZoomHover
                     :image="enhancedImage"
                     class="rounded-md outline-1 outline-offset-2 outline-dashed outline-zinc-300"
                  ></ImageZoomHover>
               </div>

               <div class="flex justify-between p-4">
                  <span
                     class="px-4 py-2 bg-primary text-primary-foreground shadow hover:bg-primary/90 rounded-md text-xs"
                     >Before: <br />{{ originalWidth }} x
                     {{ originalHeight }} px</span
                  >
                  <span
                     class="px-4 py-2 bg-primary text-primary-foreground shadow hover:bg-primary/90 rounded-md text-xs"
                     >After: <br />{{ enhancedWidth }} x
                     {{ enhancedHeight }} px</span
                  >
               </div>
            </div>
         </ImageComparison>
      </div>

      <div
         class="operations lg:col-span-1 rounded-md border relative lg:h-full lg:h-[calc(100vh-88px)]"
      >
         <h1></h1>
      </div>
   </div>

   <div
      v-else
      class="flex flex-col w-screen h-[500px] items-center justify-center gap-y-4"
   >
      <LoaderCircle class="w-10 h-10 mr-2 animate-spin" />
      <p>Loading image...</p>
   </div>
</template>

<script setup lang="ts">
   import { getImageById } from '@/services/imagesService';
   import { onMounted, ref, watch } from 'vue';
   import {
      ImageComparison,
      ImageComparisonHeader,
      ImageComparisonTitle,
      ImageComparisonContent,
   } from '@/components/ui/image-comparison';
   import { Label } from '@/components/ui/label';
   import { Switch } from '@/components/ui/switch';
   import { useRoute } from 'vue-router';
   import { LoaderCircle } from 'lucide-vue-next';
   import { ImageZoomHover } from '@/components/ui/image-zoom-hover';
   import { SCALE_FACTORS } from '@/utils/constants';

   const value = ref(0);
   watch(value, (n, o) => {
      console.log(n);
   });
   const tickLabels = Object.fromEntries(
      SCALE_FACTORS.map((value, index) => [index, value.toString()])
   );
   console.log(tickLabels);
   const originalImage = ref<string>('');
   const enhancedImage = ref<string>('');
   const scaleFactor = ref<string>('');
   const route = useRoute();
   const viewMode = ref<string>('default');

   const handleChangeViewMode = (e: unknown) => {
      if (e === true) {
         viewMode.value = 'comparison';
      } else {
         viewMode.value = 'default';
      }
   };

   const getImageSizeFromBlob = (
      blob: any
   ): Promise<{ width: number; height: number }> => {
      return new Promise((resolve, reject) => {
         const img = new Image();
         img.src = blob?.value;

         img.onload = () => {
            resolve({
               width: img.width,
               height: img.height,
            });
         };

         img.onerror = (error) => reject(error);
      });
   };
   const originalWidth = ref(0);
   const originalHeight = ref(0);
   const enhancedWidth = ref(0);
   const enhancedHeight = ref(0);

   onMounted(async () => {
      originalImage.value = await getImageById(
         route.params.original_id as string
      );
      enhancedImage.value = await getImageById(
         route.params.enhanced_id as string
      );
      scaleFactor.value = route.params.scale as string;
      const { width, height } = await getImageSizeFromBlob(originalImage);
      originalHeight.value = height;
      originalWidth.value = width;

      const { width: width1, height: height1 } = await getImageSizeFromBlob(
         enhancedImage
      );
      enhancedHeight.value = width1;
      enhancedWidth.value = height1;
   });
</script>
