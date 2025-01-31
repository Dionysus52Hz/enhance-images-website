<template>
   <h1>This is test view</h1>
   <Button @click="testSKR">Test Display Image</Button>

   <div class="w-[500px]">
      <ImageComparison>
         <ImageComparisonHeader>
            <ImageComparisonTitle>Upscale x4</ImageComparisonTitle>
         </ImageComparisonHeader>

         <ImageComparisonContent
            :left-image="'https://www.alleycat.org/wp-content/uploads/2019/03/FELV-cat.jpg'"
            :right-image="'https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Cat03.jpg/1200px-Cat03.jpg'"
         >
         </ImageComparisonContent>
      </ImageComparison>
   </div>

   <div class="p-4">
      <Card>
         <CardHeader>
            <CardTitle>Test</CardTitle>
            <CardDescription>Card Description</CardDescription>
         </CardHeader>
         <CardContent class="flex gap-x-2">
            <Card>
               <CardHeader>
                  <CardTitle>Original Image</CardTitle>
               </CardHeader>
               <CardContent>
                  <img
                     :src="imageURL"
                     alt=""
                  />
               </CardContent>
            </Card>

            <Card>
               <CardHeader>
                  <CardTitle>Downsampled Image</CardTitle>
               </CardHeader>
               <CardContent></CardContent>
            </Card>

            <Card>
               <CardHeader>
                  <CardTitle>Upsampled Image</CardTitle>
               </CardHeader>
               <CardContent></CardContent>
            </Card>
         </CardContent>
         <CardFooter> Card Footer </CardFooter>
      </Card>
   </div>
</template>

<script setup lang="ts">
   import { Button } from '@/components/ui/button';
   import {
      Card,
      CardContent,
      CardDescription,
      CardFooter,
      CardHeader,
      CardTitle,
   } from '@/components/ui/card';
   import { getImageById } from '@/services/imagesService';
   import { ref } from 'vue';
   import {
      ImageComparison,
      ImageComparisonHeader,
      ImageComparisonTitle,
      ImageComparisonContent,
   } from '@/components/ui/image-comparison';

   const imageURL = ref<undefined | string>(undefined);
   const testSKR = async () => {
      imageURL.value = await getImageById('679887c2dbcb1a686e7b57a4');
   };
</script>
