<template>
   <Dialog v-if="width < 1024">
      <div
         class="actions flex py-4 justify-end gap-x-4 px-4"
         v-if="imageToProcess"
      >
         <DialogTrigger as-child>
            <Button
               variant="ghost"
               @click="
                  (needConfirmClearQueue = true),
                     (openCustomizeOperations = false)
               "
            >
               <Trash2 />
               Clear queue</Button
            >
         </DialogTrigger>

         <DialogTrigger as-child>
            <Button
               @click="
                  (needConfirmClearQueue = false),
                     (openCustomizeOperations = true)
               "
            >
               <Bolt />
               Choose Operations
            </Button>
         </DialogTrigger>
      </div>

      <DialogContent
         class="max-w-[425px] sm:max-w-[500px] md:max-w-[600px] rounded-lg grid-rows-[auto_minmax(0,1fr)_auto] p-0 max-h-[90dvh]"
         @interact-outside="(e) => e.preventDefault()"
      >
         <DialogHeader class="p-6 pb-0">
            <DialogTitle>
               <p v-if="openCustomizeOperations === true">Choose operations</p>

               <p v-if="needConfirmClearQueue">Confirm clear queue</p>
            </DialogTitle>

            <DialogDescription></DialogDescription>
         </DialogHeader>

         <div
            v-if="needConfirmClearQueue"
            class="p-4 px-6"
         >
            <p class="text-center">
               You want to clear image from queue? This action cannot be undone.
            </p>
         </div>

         <DialogFooter
            v-if="needConfirmClearQueue"
            class="p-6 pt-0"
         >
            <DialogClose as-child>
               <Button variant="outline">Cancel</Button>
            </DialogClose>

            <DialogClose as-child>
               <Button
                  variant="destructive"
                  class="text-white"
                  @click="emit('clearQueue')"
                  >Yes, clear</Button
               >
            </DialogClose>
         </DialogFooter>

         <div
            class="grid gap-4 p-4 px-6 overflow-y-auto"
            v-if="!needConfirmClearQueue"
         >
            <div class="grid gap-y-2">
               <div
                  v-if="imageToProcess"
                  class="border rounded-lg p-4 mb-4"
               >
                  <p
                     class="font-semibold tracking-tight flex items-center gap-x-1"
                  >
                     Preview
                  </p>

                  <div
                     class="mt-3 flex justify-center rounded-md overflow-hidden"
                  >
                     <img
                        class="w-full object-contain"
                        style="image-rendering: pixelated"
                        :src="imageToProcess?.url"
                        alt=""
                     />
                  </div>
               </div>

               <form
                  class="w-full space-y-4 h-max mb-4"
                  @submit="onSubmit"
               >
                  <FormField
                     v-slot="{ componentField }"
                     name="factor"
                  >
                     <FormItem class="border rounded-lg p-4">
                        <TooltipProvider :delay-duration="200">
                           <Tooltip>
                              <p
                                 class="font-semibold tracking-tight flex items-center gap-x-1"
                              >
                                 Scale factor
                                 <TooltipTrigger as-child>
                                    <CircleHelp
                                       class="w-4 h-4 cursor-pointer"
                                    />
                                 </TooltipTrigger>
                              </p>
                              <TooltipContent class="max-w-[260px] p-4">
                                 <p class="text-sm">
                                    Selects how much to enlarge the image. For
                                    images smaller than 512 x 512, 4x is
                                    recommended.
                                 </p>
                              </TooltipContent>
                           </Tooltip>
                        </TooltipProvider>
                        <FormControl>
                           <v-slider
                              :max="SCALE_FACTORS.length - 1"
                              show-ticks="always"
                              :ticks="tickLabels"
                              :step="1"
                              tick-size="4"
                              :model-value="factorIndex"
                              thumb-label
                              track-size="6"
                              @update:model-value="
                                 (newValue) => {
                                    handleChange(newValue);
                                    emit(
                                       'changeScaleFactor',
                                       SCALE_FACTORS[newValue]
                                    );
                                 }
                              "
                              v-bind="componentField"
                           >
                              <template v-slot:thumb-label="{ modelValue }">
                                 {{ SCALE_FACTORS[modelValue] }}x
                              </template>
                           </v-slider>
                        </FormControl>
                        <FormMessage />
                     </FormItem>
                  </FormField>

                  <FormField
                     v-slot="{ componentField }"
                     type="radio"
                     name="model"
                  >
                     <FormItem class="border rounded-lg p-4">
                        <p
                           class="font-semibold tracking-tight flex items-center gap-x-1"
                        >
                           Model
                        </p>
                        <FormControl>
                           <RadioGroup
                              class="flex flex-wrap gap-x-4 gap-y-4 !mt-3"
                              v-bind="componentField"
                           >
                              <FormItem
                                 v-for="model in SR_MODELS"
                                 class="cursor-pointer flex items-center space-y-0 gap-x-3 rounded-lg bg-zinc-100 has-[:checked]:outline has-[:checked]:outline-1"
                              >
                                 <FormLabel
                                    class="cursor-pointer leading-normal px-4 py-2 grow"
                                 >
                                    {{ model.text }}
                                 </FormLabel>
                                 <FormControl class="mr-4 hidden">
                                    <RadioGroupItem :value="model.value" />
                                 </FormControl>
                              </FormItem>
                           </RadioGroup>
                        </FormControl>
                        <FormMessage />
                     </FormItem>
                  </FormField>
               </form>
            </div>
         </div>

         <DialogFooter
            class="p-6 pt-0"
            v-if="openCustomizeOperations === true"
         >
            <DialogClose as-child>
               <Button variant="outline">Cancel</Button>
            </DialogClose>

            <DialogFooter>
               <DialogClose as-child>
                  <Button
                     :disabled="props.imageToProcess === null"
                     @click="
                        startProcessing(),
                           (startProcessingOnMobileScreen = true),
                           (startProcessingOnLargeScreen = false)
                     "
                  >
                     Start processing
                  </Button>
               </DialogClose>
            </DialogFooter>
         </DialogFooter>
      </DialogContent>
   </Dialog>

   <div
      v-show="width >= 1024"
      :class="
         cn(
            'flex flex-col lg:h-full lg:max-h-[calc(100vh-56px)] px-4',
            props.class
         )
      "
      v-bind="attrs"
   >
      <h1 class="text-base uppercase font-medium py-4">Operations</h1>

      <Separator />

      <div class="mt-4 mb-[80px] overflow-y-scroll grow">
         <div
            v-if="imageToProcess"
            class="border rounded-lg p-4 mb-4"
         >
            <p class="font-semibold tracking-tight flex items-center gap-x-1">
               Preview
            </p>

            <div class="mt-3 flex justify-center rounded-md overflow-hidden">
               <img
                  class="w-full object-contain"
                  style="image-rendering: pixelated"
                  :src="imageToProcess?.url"
                  alt=""
               />
            </div>
         </div>

         <form
            class="w-full space-y-4 h-max mb-4"
            @submit="onSubmit"
         >
            <FormField
               v-slot="{ componentField }"
               name="factor"
            >
               <FormItem class="border rounded-lg p-4">
                  <TooltipProvider :delay-duration="200">
                     <Tooltip>
                        <p
                           class="font-semibold tracking-tight flex items-center gap-x-1"
                        >
                           Scale factor
                           <TooltipTrigger as-child>
                              <CircleHelp class="w-4 h-4 cursor-pointer" />
                           </TooltipTrigger>
                        </p>
                        <TooltipContent class="max-w-[260px] p-4">
                           <p class="text-sm">
                              Selects how much to enlarge the image. For images
                              smaller than 512 x 512, 4x is recommended.
                           </p>
                        </TooltipContent>
                     </Tooltip>
                  </TooltipProvider>
                  <FormControl>
                     <v-slider
                        :max="SCALE_FACTORS.length - 1"
                        show-ticks="always"
                        :ticks="tickLabels"
                        :step="1"
                        tick-size="4"
                        :model-value="factorIndex"
                        thumb-label
                        track-size="6"
                        @update:model-value="
                           (newValue) => {
                              handleChange(newValue);
                              emit(
                                 'changeScaleFactor',
                                 SCALE_FACTORS[newValue]
                              );
                           }
                        "
                        v-bind="componentField"
                     >
                        <template v-slot:thumb-label="{ modelValue }">
                           {{ SCALE_FACTORS[modelValue] }}x
                        </template>
                     </v-slider>
                  </FormControl>
                  <FormMessage />
               </FormItem>
            </FormField>

            <FormField
               v-slot="{ componentField }"
               type="radio"
               name="model"
            >
               <FormItem class="border rounded-lg p-4">
                  <p
                     class="font-semibold tracking-tight flex items-center gap-x-1"
                  >
                     Model
                  </p>
                  <FormControl>
                     <RadioGroup
                        class="flex flex-wrap gap-4 !mt-3"
                        v-bind="componentField"
                     >
                        <FormItem
                           v-for="model in SR_MODELS"
                           class="cursor-pointer flex items-center space-y-0 gap-x-3 rounded-lg bg-zinc-100 has-[:checked]:outline has-[:checked]:outline-1"
                        >
                           <FormLabel
                              class="cursor-pointer leading-normal px-4 py-2 grow"
                           >
                              {{ model.text }}
                           </FormLabel>
                           <FormControl class="mr-4 hidden">
                              <RadioGroupItem :value="model.value" />
                           </FormControl>
                        </FormItem>
                     </RadioGroup>
                  </FormControl>
                  <FormMessage />
               </FormItem>
            </FormField>
         </form>
      </div>

      <Dialog
         :open="startProcessingOnMobileScreen || startProcessingOnLargeScreen"
         @update:open="startProcessingOnMobileScreen = false"
      >
         <DialogTrigger as-child>
            <Button
               :disabled="props.imageToProcess === null"
               class="w-full py-6 mb-4"
               @click="
                  startProcessing(),
                     (startProcessingOnLargeScreen = true),
                     (startProcessingOnMobileScreen = false)
               "
               >Start processing</Button
            >
         </DialogTrigger>
         <DialogContent
            class="max-w-[500px] rounded-lg grid-rows-[auto_minmax(0,1fr)_auto] p-0 max-h-[90dvh]"
            @interact-outside="(e) => e.preventDefault()"
         >
            <DialogHeader class="p-6 pb-0">
               <DialogTitle>
                  <p class="text-xl">Processing</p>
               </DialogTitle>
               <DialogDescription></DialogDescription>
            </DialogHeader>

            <div class="grid gap-4 py-4 overflow-y-auto px-6">
               <p
                  v-if="showEnhanceResult === false"
                  class="text-center text-xl"
               >
                  No images to process
               </p>

               <div
                  v-if="isEnhancing === true && getError === false"
                  class="grid place-items-center gap-y-8"
               >
                  <p class="text-xl">{{ dialogMessage }}</p>
                  <v-progress-linear
                     v-model="progressValue"
                     :buffer-value="bufferProgressValue"
                     :height="12"
                     rounded
                     rounded-bar
                     stream
                     class="mb-1"
                  ></v-progress-linear>
               </div>

               <div
                  v-if="isEnhancing === true && getError === true"
                  class="grid place-items-center gap-y-4"
               >
                  <Frown class="w-10 h-10 mr-2" />
                  <p>Opps! Something wrong...</p>
                  <div class="flex gap-x-4">
                     <DialogClose as-child>
                        <Button variant="outline">Close</Button>
                     </DialogClose>
                     <Button @click="startProcessing">Try again</Button>
                  </div>
               </div>

               <div
                  v-if="
                     imageToProcess &&
                     isEnhancing === false &&
                     getError === false
                  "
                  class="grid place-items-center gap-y-4 text-xl"
               >
                  <p>Process is completed</p>
               </div>
            </div>
         </DialogContent>
      </Dialog>
   </div>
</template>

<script setup lang="ts">
   import {
      Dialog,
      DialogContent,
      DialogDescription,
      DialogFooter,
      DialogHeader,
      DialogTitle,
      DialogTrigger,
      DialogClose,
   } from '@/components/ui/dialog';
   import {
      Tooltip,
      TooltipContent,
      TooltipProvider,
      TooltipTrigger,
   } from '@/components/ui/tooltip';
   import {
      FormControl,
      FormField,
      FormItem,
      FormLabel,
      FormMessage,
   } from '@/components/ui/form';
   import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
   import { Separator } from '@/components/ui/separator';
   import { Button } from '@/components/ui/button';
   import { Trash2, Bolt, CircleHelp, Frown } from 'lucide-vue-next';
   import { cn } from '@/lib/utils';

   import * as z from 'zod';
   import { useForm, useField } from 'vee-validate';
   import { toTypedSchema } from '@vee-validate/zod';

   import type { Image, ServerMessage } from '@/utils/types';
   import type { HTMLAttributes } from 'vue';
   import { SR_MODELS, SCALE_FACTORS } from '@/utils/constants';

   import { onBeforeUnmount, ref, toRefs, useAttrs, watch } from 'vue';
   import { useWindowSize } from '@vueuse/core';
   import { useRouter } from 'vue-router';

   import { useEnhanceResultStore } from '@/stores/enhanceResultStore';

   const enhanceResultStore = useEnhanceResultStore();

   const { width } = useWindowSize();

   const router = useRouter();
   const attrs = useAttrs();
   defineOptions({
      inheritAttrs: false,
   });
   const props = defineProps<{
      imageToProcess: Image | null;
      class?: HTMLAttributes['class'];
   }>();
   const emit = defineEmits<{
      (e: 'enhanceStart', id: string): void;
      (e: 'enhanceEnd', id: string): void;
      (e: 'changeScaleFactor', scaleFactor: number): void;
      (e: 'clearQueue'): void;
   }>();

   const tickLabels = Object.fromEntries(
      SCALE_FACTORS.map((value, index) => [index, value.toString()])
   );

   const { imageToProcess } = toRefs(props);
   const dialogMessage = ref<string>('');
   const showEnhanceResult = ref(false);
   const isEnhancing = ref(false);
   const needConfirmClearQueue = ref(false);
   const openCustomizeOperations = ref(false);
   const getError = ref(false);
   const progressValue = ref<number>(0);
   const bufferProgressValue = ref<number>(0);
   const startProcessingOnMobileScreen = ref(false);
   const startProcessingOnLargeScreen = ref(false);

   const formSchema = toTypedSchema(
      z.object({
         factorIndex: z.number({
            required_error: 'You need to select factor',
         }),
         model: z.enum(['skr', 'nni', 'bilinear', 'bicubic'], {
            required_error: 'You need to select model',
         }),
      })
   );

   const { handleSubmit, resetForm } = useForm({
      validationSchema: formSchema,
      validateOnMount: false,
      initialValues: {
         factorIndex: 0,
         model: 'skr',
      },
   });
   const { value: factorIndex, handleChange } = useField<number>('factorIndex');

   const onSubmit = handleSubmit(async (values: any) => {
      try {
         const formData = new FormData();
         if (imageToProcess.value) {
            formData.append('image', imageToProcess.value.file);
            formData.append('name', imageToProcess.value.name);
            formData.append('size', imageToProcess.value.size.toString());
            formData.append('url', imageToProcess.value.url.toString());
            formData.append('width', imageToProcess.value.width.toString());
            formData.append('height', imageToProcess.value.height.toString());
            formData.append('model', values.model);
            formData.append(
               'scaleFactor',
               SCALE_FACTORS[values.factorIndex].toString()
            );
         }
         dialogMessage.value = 'Uploading image';
         progressValue.value = 0;
         bufferProgressValue.value = 0;

         const serverUploadMessages = ref<ServerMessage[]>([]);
         const uploadResponse = await fetch(
            'http://localhost:8000/api/v1/images/upload',
            {
               method: 'POST',
               body: formData,
            }
         );

         if (uploadResponse.body) {
            const reader = uploadResponse.body?.getReader();
            const decoder = new TextDecoder('utf-8');
            let buffer = '';

            while (true) {
               const { value, done } = await reader.read();
               if (done) break;

               buffer += decoder.decode(value, { stream: true });
               const parts = buffer.split('\n\n');

               for (const part of parts.slice(0, -1)) {
                  const line = part.trim();
                  if (line.startsWith('data: ')) {
                     const json = line.replace('data: ', '');
                     const data: ServerMessage = JSON.parse(json);
                     dialogMessage.value = data.message;
                     serverUploadMessages.value.push(data);

                     if (data.message === 'Uploading image') {
                        progressValue.value = 0;
                        bufferProgressValue.value = 0;
                     } else if (data.message === 'Upload completed') {
                        progressValue.value = 10;
                        bufferProgressValue.value = 20;
                     }
                  }
               }

               buffer = parts[parts.length - 1];
            }
         } else {
            throw new Error('Response body is null.');
         }

         if (uploadResponse) {
            const serverEnhanceMessages = ref<ServerMessage[]>([]);
            const enhanceResponse = await fetch(
               'http://localhost:8000/api/v1/enhancers',
               {
                  method: 'POST',
                  body: formData,
               }
            );
            if (enhanceResponse.body) {
               const reader = enhanceResponse.body?.getReader();
               const decoder = new TextDecoder('utf-8');
               let buffer = '';

               while (true) {
                  const { value, done } = await reader.read();
                  if (done) break;

                  buffer += decoder.decode(value, { stream: true });
                  const parts = buffer.split('\n\n');

                  for (const part of parts.slice(0, -1)) {
                     const line = part.trim();
                     if (line.startsWith('data: ')) {
                        const json = line.replace('data: ', '');
                        const data: ServerMessage = JSON.parse(json);
                        dialogMessage.value = data.message;
                        serverEnhanceMessages.value.push(data);

                        switch (values.model) {
                           case 'skr':
                              if (
                                 data.message === 'Computing initial gradients'
                              ) {
                                 progressValue.value = 20;
                                 bufferProgressValue.value = 40;
                              } else if (
                                 data.message ===
                                 'Calculating steering matrices'
                              ) {
                                 progressValue.value = 40;
                                 bufferProgressValue.value = 60;
                              } else if (
                                 data.message ===
                                 'Applying steering kernel regression'
                              ) {
                                 progressValue.value = 60;
                                 bufferProgressValue.value = 80;
                              } else if (
                                 data.message === 'Processing completed!'
                              ) {
                                 progressValue.value = 100;
                              }
                              break;

                           case 'nni':
                              if (data.message === 'Grid mapping') {
                                 progressValue.value = 20;
                                 bufferProgressValue.value = 30;
                              } else if (
                                 data.message ===
                                 'Specifying pixels to interpolate'
                              ) {
                                 progressValue.value = 30;
                                 bufferProgressValue.value = 40;
                              } else if (
                                 data.message ===
                                 'Constructing Delaunay triangulation'
                              ) {
                                 progressValue.value = 40;
                                 bufferProgressValue.value = 60;
                              } else if (
                                 data.message === 'Starting interpolate'
                              ) {
                                 progressValue.value = 60;
                                 bufferProgressValue.value = 90;
                              } else if (
                                 data.message === 'Processing completed!'
                              ) {
                                 progressValue.value = 100;
                              }
                              break;

                           case 'bilinear':
                              if (data.message === 'Enhancing resolution') {
                                 progressValue.value = 30;
                                 bufferProgressValue.value = 50;
                              } else if (
                                 data.message === 'Processing completed!'
                              ) {
                                 progressValue.value = 100;
                              }
                              break;
                           case 'bicubic':
                              if (data.message === 'Enhancing resolution') {
                                 progressValue.value = 30;
                                 bufferProgressValue.value = 50;
                              } else if (
                                 data.message === 'Processing completed!'
                              ) {
                                 progressValue.value = 100;
                              }
                              break;
                           default:
                              break;
                        }
                     }
                  }

                  buffer = parts[parts.length - 1];
               }
            } else {
               throw new Error('Response body is null.');
            }

            const lastEnhanceResponse: ServerMessage =
               serverEnhanceMessages.value[
                  serverEnhanceMessages.value.length - 1
               ];
            if (
               lastEnhanceResponse.data &&
               lastEnhanceResponse.statusCode === 200
            ) {
               isEnhancing.value = false;
               showEnhanceResult.value = true;

               enhanceResultStore.setEnhanceResultState({
                  lr: lastEnhanceResponse.data.lr.url,
                  sr: lastEnhanceResponse.data.sr.url,
               });

               router.push({
                  name: 'results-view',
                  params: {
                     model: values.model,
                     scale: SCALE_FACTORS[values.factorIndex].toString() + 'x',
                  },
               });

               progressValue.value = 0;
               bufferProgressValue.value = 0;
               serverUploadMessages.value = [];
               serverEnhanceMessages.value = [];
            }
         }
         resetForm();
      } catch (error) {
         console.log('Error:', error);
         getError.value = true;
      }
   });

   const startProcessing = () => {
      if (imageToProcess) {
         isEnhancing.value = true;
         getError.value = false;
         onSubmit();
         showEnhanceResult.value = true;
      }
   };

   onBeforeUnmount(() => {
      startProcessingOnMobileScreen.value = false;
   });
</script>

<style scope>
   .v-progress-linear__buffer {
      border-radius: 20px;
   }
</style>
