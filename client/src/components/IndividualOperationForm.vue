<template>
   <form
      @submit="onSubmit"
      class="flex items-end gap-x-3 mt-3"
   >
      <div>
         <img
            :src="props.image.url"
            alt=""
            class="w-[60px] bg-zinc-200 object-contain"
         />
      </div>

      <div class="grow grid grid-cols-2 gap-x-3">
         <FormField
            v-slot="{ componentField }"
            name="factor"
         >
            <FormItem>
               <FormLabel>Scale factor</FormLabel>

               <Select v-bind="componentField">
                  <FormControl class="text-ellipsis overflow-hidden">
                     <SelectTrigger class="text-ellipsis overflow-hidden">
                        <SelectValue
                           class="text-ellipsis overflow-hidden"
                           placeholder="Select scale factor"
                        />
                     </SelectTrigger>
                  </FormControl>
                  <SelectContent>
                     <SelectGroup>
                        <SelectItem
                           v-for="factor in SCALE_FACTORS"
                           :value="factor.toString()"
                        >
                           {{ factor }}x
                        </SelectItem>
                     </SelectGroup>
                  </SelectContent>
               </Select>

               <FormMessage />
            </FormItem>
         </FormField>

         <FormField
            v-slot="{ componentField }"
            name="model"
         >
            <FormItem class="grow">
               <FormLabel>Model</FormLabel>

               <Select v-bind="componentField">
                  <FormControl>
                     <SelectTrigger class="grow">
                        <SelectValue placeholder="Select model" />
                     </SelectTrigger>
                  </FormControl>
                  <SelectContent>
                     <SelectGroup>
                        <SelectItem
                           v-for="model in SR_MODELS"
                           :value="model.value"
                        >
                           {{ model.text }}
                        </SelectItem>
                     </SelectGroup>
                  </SelectContent>
               </Select>

               <FormMessage />
            </FormItem>
         </FormField>
      </div>
   </form>
</template>

<script setup lang="ts">
   import { useForm } from 'vee-validate';
   import { toTypedSchema } from '@vee-validate/zod';
   import * as z from 'zod';
   import {
      FormControl,
      FormField,
      FormItem,
      FormLabel,
      FormMessage,
   } from '@/components/ui/form';
   import {
      Select,
      SelectContent,
      SelectGroup,
      SelectItem,
      SelectTrigger,
      SelectValue,
   } from '@/components/ui/select';
   import { SCALE_FACTORS, SR_MODELS } from '@/utils/constants';
   import type { Image, ImageToProcess } from '@/utils/types';
   import { defineExpose } from 'vue';
   import { uploads } from '@/services/imagesService';

   const formSchema = toTypedSchema(
      z.object({
         factor: z.enum(['2', '4', '8'], {
            required_error: 'You need to select factor',
         }),
         model: z.enum(['SKR', 'MS_LapSRN'], {
            required_error: 'You need to select model',
         }),
      })
   );

   const props = defineProps<{
      image: Image;
   }>();

   const { handleSubmit, resetForm } = useForm({
      validateOnMount: false,
      validationSchema: formSchema,
   });

   const onSubmit = handleSubmit(async (values) => {
      try {
         const data: ImageToProcess = {
            ...values,
            image: props.image,
         };

         const formData = new FormData();
         formData.append('files', data.image.file);
         formData.append('names', data.image.name);
         formData.append('urls', data.image.url);
         formData.append('sizes', data.image.size.toString());
         formData.append('widths', data.image.width.toString());
         formData.append('heights', data.image.height.toString());
         formData.append('models', data.model);
         formData.append('factors', data.factor);

         const response = await uploads(formData);

         console.log(response);
         resetForm();
      } catch (error) {
         console.log('Error:', error);
      }
   });

   defineExpose({
      onSubmit,
   });
</script>
