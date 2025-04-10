<template>
   <div
      class="relative overflow-hidden"
      :class="
         cn('text-xl font-semibold leading-none tracking-tight', props.class)
      "
   >
      <!-- Ảnh zoom -->
      <div
         ref="container"
         class="relative overflow-hidden cursor-none"
         @mousemove="handleMouseMove"
         @mouseleave="handleMouseLeave"
      >
         <img
            ref="imageRef"
            :src="props.image"
            alt="Zoom Image"
            class="w-full h-full object-cover transition-transform duration-200"
            :class="{
               'scale-[3]': position.active,
               pixelated: props.displayMode == 'pixelated',
            }"
            :style="
               position.active
                  ? {
                       transformOrigin: `${
                          (position.x / containerWidth) * 100
                       }% ${(position.y / containerHeight) * 100}%`,
                    }
                  : {}
            "
         />
      </div>

      <!-- Con trỏ giả -->
      <div
         ref="cursor"
         class="absolute border border-white rounded-full top-0 left-0 pointer-events-none"
         :style="customCursorStyle"
      ></div>
   </div>
</template>

<script setup lang="ts">
   import type { HTMLAttributes, CSSProperties } from 'vue';
   import { cn } from '@/lib/utils';
   import { ref, computed, onMounted, onBeforeMount, watch } from 'vue';

   const props = defineProps<{
      class?: HTMLAttributes['class'];
      image: string | undefined;
      displayMode?: string;
   }>();

   const emit = defineEmits<{
      (e: 'width', width: number): void;
      (e: 'height', height: number): void;
   }>();

   const imageRef = ref<HTMLImageElement | null>(null);
   const container = ref<HTMLInputElement | null>(null);
   const cursor = ref<HTMLInputElement | null>(null);

   const position = ref({ x: 0, y: 0, active: false });
   const active = ref(false);
   const handleSize = ref(40);
   const containerHeight = ref(0);
   const containerWidth = ref(0);
   const cursorXPosition = ref(0);
   const cursorYPosition = ref(0);
   const cursorXFromViewport = ref(0);
   const cursorYFromViewport = ref(0);

   const handleMouseMove = (event: MouseEvent | TouchEvent | KeyboardEvent) => {
      if (!container.value) return;

      const { left, top, width, height } =
         container.value!.getBoundingClientRect();
      cursorXFromViewport.value = left;
      cursorYFromViewport.value = top;
      containerHeight.value = height;
      containerWidth.value = width;
      active.value = true;
      const e = event as TouchEvent;
      // @ts-expect-error
      const x = e.pageX - cursorXFromViewport.value;
      // @ts-expect-error
      const y = e.pageY - cursorYFromViewport.value;

      position.value = { x, y, active: true };
      cursorXPosition.value = x / containerWidth.value;
      cursorYPosition.value = y / containerHeight.value;
   };

   const handleMouseLeave = () => {
      position.value.active = false;
      active.value = false;
   };

   const customCursorStyle = computed((): CSSProperties => {
      return {
         width: `${handleSize.value}px`,
         height: `${handleSize.value}px`,
         transform: `translate(${position.value.x - handleSize.value / 2}px, ${
            position.value.y - handleSize.value / 2
         }px)`,
         boxShadow: '0 2px 3px 0 rgb(0 0 0 / 0.1)',
      };
   });
</script>

<style scoped>
   .pixelated {
      image-rendering: pixelated;
   }
</style>
