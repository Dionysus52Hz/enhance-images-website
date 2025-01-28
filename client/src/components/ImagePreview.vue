<template>
   <div
      v-if="images.length > 0"
      class="border rounded-lg"
   >
      <Table>
         <TableCaption class="my-4">List of your imported images.</TableCaption>

         <TableHeader>
            <TableRow>
               <TableHead class="min-w-[150px]"> Thumbnail </TableHead>

               <TableHead>Input</TableHead>

               <TableHead>Output</TableHead>

               <TableHead> Status </TableHead>

               <TableHead></TableHead>
            </TableRow>
         </TableHeader>

         <draggable
            v-model="images"
            item-key="images-queue"
            @start="dragging = true"
            @end="dragging = false"
            class="grow cursor-grab"
            tag="tbody"
            :animation="300"
         >
            <template #item="{ element, index }">
               <TableRow :key="element.name">
                  <TableCell
                     class="font-medium w-[150px]"
                     @click="console.log(element)"
                  >
                     <img
                        :src="element.url"
                        alt=""
                        class="object-contain"
                     />
                  </TableCell>

                  <TableCell class="min-w-[150px]">
                     <div class="grid text-sm">
                        <span>Resolution</span>
                        <span class="mt-1 mb-2 font-medium"
                           >{{ element.width }} x {{ element.height }} px</span
                        >
                        <span>Size</span>
                        <span class="mt-1 mb-2 font-medium"
                           >{{ (element.size / 1024).toFixed(2) }} KB</span
                        >
                     </div>
                  </TableCell>

                  <TableCell class="min-w-[150px]">
                     <div class="grid text-sm">
                        <span>Resolution</span>
                        <span class="mt-1 mb-2 font-medium"
                           >{{ element.width }} x {{ element.height }} px</span
                        >
                        <span>Size</span>
                        <span class="mt-1 mb-2 font-medium"
                           >{{ (element.size / 1024).toFixed(2) }} KB</span
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
                                 @click="removeImage(index)"
                              >
                                 <Trash class="w-5 h-5" />
                              </Button>
                           </TooltipTrigger>
                           <TooltipContent>
                              <p class="text-[13px]">Remove from queue</p>
                           </TooltipContent>
                        </Tooltip>
                     </TooltipProvider>
                  </TableCell>
               </TableRow>
            </template>
         </draggable>
      </Table>
   </div>

   <Dialog @update:open="operationsMode = 'same-operations'">
      <div
         class="actions flex py-4 justify-end gap-x-4"
         v-if="images.length > 0"
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
      >
         <DialogHeader class="p-6 pb-0">
            <DialogTitle>
               <p
                  v-if="needConfirmClearQueue === true"
                  class="leading-normal text-center mt-4"
               >
                  Are you sure you want to remove all images?
               </p>

               <p v-if="openCustomizeOperations === true">
                  Customize operations
               </p>
            </DialogTitle>

            <DialogDescription></DialogDescription>
         </DialogHeader>

         <div class="grid gap-4 py-4 overflow-y-auto px-6">
            <p
               v-if="needConfirmClearQueue === true"
               class="text-sm text-center"
            >
               This will remove all images from queue permanently. You cannot
               undo this action.
            </p>

            <div
               v-if="openCustomizeOperations === true"
               class="grid gap-y-2"
            >
               <form
                  class="w-full space-y-6"
                  @submit="onSubmit"
               >
                  <!-- Operations mode field -->
                  <FormField
                     v-slot="{ componentField }"
                     type="radio"
                     name="mode"
                  >
                     <FormItem class="space-y-3 border rounded-lg p-4">
                        <p class="font-semibold tracking-tight">
                           Operations mode
                        </p>

                        <FormControl>
                           <RadioGroup
                              class="flex flex-col space-y-1"
                              v-bind="componentField"
                           >
                              <FormItem
                                 class="cursor-pointer flex items-center space-y-0 gap-x-3 rounded-lg bg-zinc-100 has-[:checked]:outline has-[:checked]:outline-1"
                                 @click="
                                    (operationsMode = 'same-operations'),
                                       (currentSchema = 0)
                                 "
                              >
                                 <FormLabel
                                    class="cursor-pointer leading-normal px-4 py-2 grow"
                                 >
                                    Use the same operations for every image
                                 </FormLabel>

                                 <FormControl class="mr-4">
                                    <RadioGroupItem value="same-operations" />
                                 </FormControl>
                              </FormItem>

                              <FormItem
                                 class="cursor-pointer flex items-center space-y-0 gap-x-3 rounded-lg bg-zinc-100 has-[:checked]:outline has-[:checked]:outline-1"
                                 @click="
                                    (operationsMode = 'separate-operations'),
                                       (currentSchema = 1)
                                 "
                              >
                                 <FormLabel
                                    class="cursor-pointer leading-normal px-4 py-2 grow"
                                    >Use separate operations for every image
                                 </FormLabel>

                                 <FormControl class="mr-4">
                                    <RadioGroupItem
                                       value="separate-operations"
                                    />
                                 </FormControl>
                              </FormItem>
                           </RadioGroup>
                        </FormControl>
                        <FormMessage />
                     </FormItem>
                  </FormField>

                  <!-- Scale factor field -->
                  <FormField
                     v-slot="{ componentField }"
                     type="radio"
                     name="factor"
                     v-if="operationsMode === 'same-operations'"
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
                     v-if="operationsMode === 'same-operations'"
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

                  <!-- Separate operations field -->

                  <div
                     class="border rounded-lg p-4"
                     v-if="operationsMode === 'separate-operations'"
                  >
                     <p
                        class="font-semibold tracking-tight flex items-center gap-x-1"
                     >
                        Customize operations
                     </p>
                     <IndividualOperationForm
                        v-for="image in images"
                        :key="image.name"
                        :image="image"
                        ref="individualOperationFormRefs"
                     ></IndividualOperationForm>
                  </div>
               </form>
            </div>
         </div>

         <DialogFooter
            class="p-6 pt-0"
            v-if="needConfirmClearQueue === true"
         >
            <DialogClose as-child>
               <Button variant="outline">Cancel</Button>
            </DialogClose>

            <DialogClose as-child>
               <Button
                  class="bg-red-600"
                  @click="removeAllImages"
               >
                  Yes, remove
               </Button>
            </DialogClose>
         </DialogFooter>

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
      Dialog,
      DialogContent,
      DialogDescription,
      DialogFooter,
      DialogHeader,
      DialogTitle,
      DialogTrigger,
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
   import { toTypedSchema } from '@vee-validate/zod';
   import { useForm } from 'vee-validate';
   import { computed, useTemplateRef } from 'vue';
   import * as z from 'zod';
   import { Button } from '@/components/ui/button';
   import draggable from 'vuedraggable';
   import { onMounted, ref } from 'vue';
   import { Trash, Trash2, Bolt, CircleHelp } from 'lucide-vue-next';
   import type { Image } from '@/utils/types';
   import DialogClose from './ui/dialog/DialogClose.vue';
   import { SR_MODELS, SCALE_FACTORS } from '@/utils/constants';
   import IndividualOperationForm from '@/components/IndividualOperationForm.vue';
   import { uploads } from '@/services/imagesService';

   const dragging = ref(false);
   const props = defineProps<{
      imagesQueue: Image[] | [];
   }>();
   const images = ref<Image[]>([]);
   const needConfirmClearQueue = ref(false);
   const openCustomizeOperations = ref(false);
   const operationsMode = ref('same-operations');

   const removeImage = (index: number) => {
      images.value.splice(index, 1);
   };
   const removeAllImages = () => {
      images.value.splice(0);
   };

   const formSchema = toTypedSchema(
      z.object({
         mode: z.enum(['same-operations', 'separate-operations'], {
            required_error: 'You need to select mode.',
         }),
         factor: z.enum(['2', '4', '8'], {
            required_error: 'You need to select factor',
         }),
         model: z.enum(['SKR', 'MS_LapSRN'], {
            required_error: 'You need to select model',
         }),
      })
   );

   const formSchema2 = toTypedSchema(
      z.object({
         mode: z.enum(['same-operations', 'separate-operations'], {
            required_error: 'You need to select mode.',
         }),
      })
   );

   const currentSchema = ref(0);
   const schema = computed(() => {
      return currentSchema.value === 0 ? formSchema : formSchema2;
   });

   const { handleSubmit, resetForm } = useForm({
      validationSchema: schema,
      validateOnMount: false,
   });

   const individualOperationFormRefs = useTemplateRef(
      'individualOperationFormRefs'
   );

   const onSubmit = handleSubmit(async (values: any) => {
      try {
         // Separate operations mode
         if (individualOperationFormRefs.value) {
            individualOperationFormRefs.value.forEach((r) => {
               r?.onSubmit();
            });
         }
         // Same operations mode
         else {
            const formData = new FormData();
            images.value.forEach((image) => {
               formData.append('files', image.file);
               formData.append('names', image.name);
               formData.append('sizes', image.size.toString());
               formData.append('urls', image.url.toString());
               formData.append('widths', image.width.toString());
               formData.append('heights', image.height.toString());
               formData.append('models', values.model);
               formData.append('factors', values.factor);
            });

            const response = await uploads(formData);

            console.log(response);
         }
      } catch (error) {
         console.log('Error:', error);
      }

      resetForm();
   });

   const startProcessing = () => {
      onSubmit();
   };

   onMounted(() => {
      images.value = props.imagesQueue;
   });
</script>
