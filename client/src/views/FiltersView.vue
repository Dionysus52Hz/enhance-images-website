<template>
   <h1>This is test view</h1>
   <Button @click="testSKR">Test Display Image</Button>
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

   const imageURL = ref<undefined | string>(undefined);
   const testSKR = async () => {
      imageURL.value = await getImageById('679887c2dbcb1a686e7b57a4');
   };
</script>
