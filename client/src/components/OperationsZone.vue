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
               Customize Operations
            </Button>
         </DialogTrigger>
      </div>

      <DialogContent
         class="max-w-[425px] rounded-lg grid-rows-[auto_minmax(0,1fr)_auto] p-0 max-h-[90dvh]"
         @interact-outside="(e) => e.preventDefault()"
      >
         <DialogHeader class="p-6 pb-0">
            <DialogTitle>
               <p v-if="openCustomizeOperations === true">
                  Customize operations
               </p>
            </DialogTitle>

            <DialogDescription></DialogDescription>
         </DialogHeader>

         <div class="grid gap-4 py-4 overflow-y-auto px-6">
            <div
               v-if="openCustomizeOperations === true"
               class="grid gap-y-2"
            >
               <form
                  class="w-full space-y-6"
                  @submit="onSubmit"
               >
                  <!-- Scale factor field -->
                  <FormField
                     v-slot="{ componentField }"
                     type="radio"
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
                           <RadioGroup
                              class="flex space-x-2 !mt-3"
                              v-bind="componentField"
                           >
                              <FormItem
                                 v-for="factor in SCALE_FACTORS"
                                 class="cursor-pointer flex items-center space-y-0 gap-x-3 rounded-lg bg-zinc-100 has-[:checked]:outline has-[:checked]:outline-1 aspect-square"
                              >
                                 <FormLabel
                                    class="leading-normal px-2.5 cursor-pointer"
                                 >
                                    {{ factor }}x
                                 </FormLabel>
                                 <FormControl class="hidden">
                                    <RadioGroupItem
                                       :value="factor.toString()"
                                    />
                                 </FormControl>
                              </FormItem>
                           </RadioGroup>
                        </FormControl>
                        <FormMessage />
                     </FormItem>
                  </FormField>

                  <!-- Model field -->
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
                              class="flex space-x-2 !mt-3"
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
                                    <RadioGroupItem
                                       :value="model.value"
                                       :disabled="props.imageToProcess === null"
                                    />
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
               <Button @click="startProcessing"> Start processing </Button>
            </DialogFooter>
         </DialogFooter>
      </DialogContent>
   </Dialog>

   <div
      v-if="width >= 1024"
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
                        class="flex space-x-2 !mt-3"
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

      <Dialog>
         <DialogTrigger as-child>
            <Button
               :disabled="props.imageToProcess === null"
               class="w-full py-6 mb-4"
               @click="startProcessing"
               >Start processing</Button
            >
         </DialogTrigger>
         <DialogContent
            class="max-w-[500px] rounded-lg grid-rows-[auto_minmax(0,1fr)_auto] p-0 max-h-[90dvh]"
            @interact-outside="(e) => e.preventDefault()"
         >
            <DialogHeader class="p-6 pb-0">
               <DialogTitle>
                  <p class="text-xl">Processing...</p>
               </DialogTitle>
               <DialogDescription></DialogDescription>
            </DialogHeader>

            <div class="grid gap-4 py-4 overflow-y-auto px-6">
               <p v-if="showEnhanceResult === false">No images to process</p>

               <div
                  v-if="isEnhancing === true && getError === false"
                  class="grid place-items-center gap-y-4"
               >
                  <LoaderCircle class="w-10 h-10 mr-2 animate-spin" />
                  <p>Waiting is happiness...</p>
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
                  v-if="isEnhancing === false && getError === false"
                  class="grid place-items-center gap-y-4"
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
   import {
      Trash2,
      Bolt,
      CircleHelp,
      LoaderCircle,
      Frown,
   } from 'lucide-vue-next';
   import { cn } from '@/lib/utils';

   import * as z from 'zod';
   import { useForm, useField } from 'vee-validate';
   import { toTypedSchema } from '@vee-validate/zod';

   import type { Image } from '@/utils/types';
   import type { HTMLAttributes } from 'vue';
   import { SR_MODELS, SCALE_FACTORS } from '@/utils/constants';

   import { ref, toRefs, useAttrs } from 'vue';
   import { useWindowSize } from '@vueuse/core';
   import { useRouter } from 'vue-router';

   import { uploads } from '@/services/imagesService';
   import { enhancing } from '@/services/enhancerService';
   import { getImageById } from '@/services/imagesService';

   const { width, height } = useWindowSize();
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
   }>();

   const tickLabels = Object.fromEntries(
      SCALE_FACTORS.map((value, index) => [index, value.toString()])
   );

   const { imageToProcess } = toRefs(props);
   const showEnhanceResult = ref(false);
   const isEnhancing = ref(false);
   const needConfirmClearQueue = ref(false);
   const openCustomizeOperations = ref(false);
   const getError = ref(false);

   const formSchema = toTypedSchema(
      z.object({
         factorIndex: z.number({
            required_error: 'You need to select factor',
         }),
         model: z.enum(['skr', 'nni', 'bilinear'], {
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
         const uploadResponse = await uploads(formData);

         console.log(uploadResponse);
         if (uploadResponse.data) {
            const enhanceResponse = await enhancing(formData);

            isEnhancing.value = false;
            showEnhanceResult.value = true;

            console.log(enhanceResponse);
            // router.push({
            //    name: 'results-view',
            //    params: {
            //       scale: SCALE_FACTORS[values.factorIndex].toString(),
            //       original_id: id,
            //       enhanced_id: response.image_id,
            //    },
            // });
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
</script>
