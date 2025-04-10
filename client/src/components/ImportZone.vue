<template>
   <div
      class="browse-file my-4 rounded-lg border border-dashed border-2 px-6 py-12 cursor-pointer grid place-items-center group text-base font-medium hover:bg-zinc-100 ease-in-out duration-500"
      @click="fileInputRef?.click()"
   >
      <input
         type="file"
         ref="fileInput"
         class="hidden"
         accept="image/jpeg, image/jpg, image/png"
         @change="handleFileChange"
      />
      <div
         class="icon-effect flex relative justify-center h-[60px] w-full mb-6"
      >
         <svg
            v-for="i in 3"
            class="absolute group-hover:first:-rotate-12 group-hover:first:-translate-x-[50px] group-hover:first:translate-y-3 group-hover:last:rotate-12 group-hover:last:translate-x-[50px] group-hover:last:translate-y-3 [&:not(:nth-child(2))]:opacity-20 [&:nth-child(2)]:z-40 ease-in-out duration-500 origin-bottom"
            width="60"
            height="60"
            viewBox="0 0 60 60"
            fill="none"
            :key="i"
         >
            <mask
               id="mask0_873_3371"
               maskUnits="userSpaceOnUse"
               x="0"
               y="0"
               width="60"
               height="60"
               style="mask-type: alpha"
            >
               <rect
                  width="60"
                  height="60"
                  rx="6"
                  fill="#EEEEFF"
               ></rect>
            </mask>
            <g mask="url(#mask0_873_3371)">
               <rect
                  width="60"
                  height="60"
                  rx="6"
                  fill="#1C1D24"
               ></rect>
               <circle
                  cx="21"
                  cy="18"
                  r="6"
                  fill="#E6E6FF"
               ></circle>
               <rect
                  opacity="0.3"
                  x="10.7969"
                  y="34"
                  width="60"
                  height="60"
                  rx="6"
                  transform="rotate(45.503 10.7969 34)"
                  fill="#E6E6FF"
               ></rect>
               <rect
                  x="38.7969"
                  y="26"
                  width="60"
                  height="60"
                  rx="6"
                  transform="rotate(45.503 38.7969 26)"
                  fill="#E6E6FF"
               ></rect>
            </g>
         </svg>
      </div>

      <h3 class="mt-1 mb-2">Drop your images</h3>
      <h3 class="mb-2">
         or
         <span>browse</span>
      </h3>
      <h4 class="text-sm text-zinc-400">JPEG, JPG, PNG up to 50MB</h4>
   </div>

   <!-- <ImagePreview
      @enhance-start="(e) => emit('enhanceStart', e)"
      @enhance-end="(e) => emit('enhanceEnd', e)"
      :image-to-process="imageToProcess"
   ></ImagePreview> -->

   <div
      v-if="imageToProcess !== null"
      class="border rounded-lg"
   >
      <Table>
         <TableCaption class="my-4">Preview your imported image.</TableCaption>

         <TableHeader>
            <TableRow>
               <TableHead class="min-w-[150px]"> Thumbnail </TableHead>

               <TableHead>Input</TableHead>

               <TableHead>Output</TableHead>

               <TableHead> Status </TableHead>

               <TableHead></TableHead>
            </TableRow>
         </TableHeader>

         <TableRow>
            <TableCell class="font-medium w-[150px]">
               <img
                  :src="imageToProcess.url"
                  alt=""
                  class="object-contain"
               />
            </TableCell>

            <TableCell class="min-w-[150px]">
               <div class="grid text-sm">
                  <span>Resolution</span>
                  <span class="mt-1 mb-2 font-medium"
                     >{{ imageToProcess.width }} x
                     {{ imageToProcess.height }} px</span
                  >
                  <span>Size</span>
                  <span class="mt-1 mb-2 font-medium"
                     >{{ (imageToProcess.size / 1024).toFixed(2) }} KB</span
                  >
               </div>
            </TableCell>

            <TableCell class="min-w-[150px]">
               <div class="grid text-sm">
                  <span>Resolution</span>
                  <span class="mt-1 mb-2 font-medium"
                     >{{ imageToProcess.width * props.scaleFactor }} x
                     {{ imageToProcess.height * props.scaleFactor }} px</span
                  >
                  <span>Size</span>
                  <span class="mt-1 mb-2 font-medium"
                     >{{
                        (
                           (imageToProcess.size / 1024) *
                           Math.pow(props.scaleFactor, 2)
                        ).toFixed(2)
                     }}
                     KB</span
                  >
               </div>
            </TableCell>

            <TableCell> Ready to process </TableCell>

            <TableCell>
               <TooltipProvider :delay-duration="200">
                  <Tooltip>
                     <TooltipTrigger as-child>
                        <Button
                           variant="ghost"
                           size="icon"
                           @click="removeImage(), emit('clearQueue')"
                        >
                           <Trash class="w-5 h-5" />
                        </Button>
                     </TooltipTrigger>
                     <TooltipContent>
                        <p class="text-[13px]">Clear image</p>
                     </TooltipContent>
                  </Tooltip>
               </TooltipProvider>
            </TableCell>
         </TableRow>
      </Table>
   </div>
</template>

<script setup lang="ts">
   import {
      Table,
      TableCaption,
      TableCell,
      TableHead,
      TableHeader,
      TableRow,
   } from '@/components/ui/table';
   import {
      Tooltip,
      TooltipContent,
      TooltipProvider,
      TooltipTrigger,
   } from '@/components/ui/tooltip';
   import { Button } from '@/components/ui/button';
   import { Trash } from 'lucide-vue-next';
   import { ref, useTemplateRef } from 'vue';
   import type { Image } from '@/utils/types';

   const emit = defineEmits<{
      (e: 'imported', image: Image): void;
      (e: 'clearQueue'): void;
   }>();
   const props = defineProps<{
      scaleFactor: number;
   }>();
   const fileInputRef = useTemplateRef('fileInput');
   const imageToProcess = ref<Image | null>(null);

   const maxFileSize = 1 * 1024 * 1024;
   const handleFileChange = (event: Event) => {
      const target = event.target as HTMLInputElement;
      if (target.files && target.files.length > 0) {
         const file = target.files[0];
         previewImage(file);
      }
   };

   const previewImage = (file: File) => {
      const validTypes = ['image/jpeg', 'image/png', 'image/jpg'];
      if (validTypes.includes(file.type)) {
         if (file.size > maxFileSize) {
            alert('File quá lớn. Vui lòng chọn file dưới 1MB.');
            return;
         }

         const img = new Image();
         const reader = new FileReader();
         reader.onload = (e) => {
            img.src = e.target?.result as string;
         };

         img.onload = () => {
            const image: Image = {
               file: file,
               url: img.src,
               name: file.name,
               size: file.size,
               width: img.width,
               height: img.height,
            };
            imageToProcess.value = image;
            emit('imported', image);
         };
         reader.readAsDataURL(file);
      } else {
         alert('Vui lòng chọn file ảnh định dạng JPEG, JPG hoặc PNG.');
      }
   };

   const removeImage = () => {
      console.log(12345);
      imageToProcess.value = null;
   };

   defineExpose({ removeImage });
</script>
