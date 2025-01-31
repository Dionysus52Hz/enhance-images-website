<template>
   <div :class="cn('p-6 pt-0 grid', props.class)">
      <div
         :id="componentId"
         ref="containerRef"
         class="flex relative overflow-hidden w-100"
         tabindex="0"
         data-testid="vci-container"
         :style="containerStyle"
         @touchstart="startSliding"
         @touchend="finishSliding"
         @mousedown="startSliding"
         @mouseup="finishSliding"
      >
         <img
            class="flex absolute object-contain h-100"
            ref="leftImageRef"
            :src="leftImage"
            :alt="leftImageAlt"
            :style="leftImageStyle"
         />
         <img
            class="flex absolute object-contain h-100"
            ref="rightImageRef"
            :src="rightImage"
            :alt="rightImageAlt"
            :style="rightImageStyle"
         />

         <div
            class="slider absolute flex justify-center items-center"
            :style="sliderStyle"
         >
            <div
               class="slider-line flex-initial shadow-sm"
               :style="lineStyle"
            ></div>
            <div
               class="handle absolute flex flex-[1_0_auto] jusitfy-center items-center rounded-full border border-white shadow-sm"
               :style="handleDefaultStyle"
            ></div>
         </div>
      </div>

      <div class="flex justify-between py-4">
         <span
            class="px-4 py-2 bg-primary text-primary-foreground shadow hover:bg-primary/90 rounded-md text-xs"
            >Before: <br />{{ leftImageRef?.naturalWidth }} x
            {{ leftImageRef?.naturalHeight }} px</span
         >
         <span
            class="px-4 py-2 bg-primary text-primary-foreground shadow hover:bg-primary/90 rounded-md text-xs"
            >After: <br />{{ rightImageRef?.naturalWidth }} x
            {{ rightImageRef?.naturalHeight }} px</span
         >
      </div>

      <div class="grid grid-cols-2 h-[200px]">
         <div
            class="block relative overflow-hidden h-100 bg-no-repeat"
            :style="zoomLeftImageStyle"
         >
            <img
               class="absolute object-cover object-center w-100 hidden"
               :src="leftImage"
               :alt="leftImageAlt"
            />
         </div>

         <div
            class="block relative overflow-hidden h-100 bg-no-repeat"
            :style="zoomRightImageStyle"
         >
            <img
               class="absolute object-cover object-center w-100 hidden"
               :src="rightImage"
               :alt="rightImageAlt"
            />
         </div>
      </div>
   </div>
</template>

<script setup lang="ts">
   import type { CSSProperties, HTMLAttributes } from 'vue';
   import { cn } from '@/lib/utils';
   import {
      computed,
      getCurrentInstance,
      onBeforeUnmount,
      onMounted,
      ref,
      toRefs,
      watch,
   } from 'vue';

   export interface ImageComparisonProps {
      class?: HTMLAttributes['class'];
      cursorXPercentage?: number;
      cursorYPercentage?: number;
      handle?: string | number | boolean;
      handleSize?: number;
      hover?: boolean;
      leftImage: string;
      leftImageAlt?: string;
      onSliderPositionChange?: (position: number) => void;
      onCursorPositionChange?: (x: number, y: number) => void;
      rightImage: string;
      rightImageAlt?: string;
      sliderLineColor?: string;
      sliderLineWidth?: number;
      sliderPositionPercentage?: number;
      vertical?: boolean;
      zoom?: number;
   }

   const props = withDefaults(defineProps<ImageComparisonProps>(), {
      class: '',
      cursorXPercentage: 0,
      cursorYPercentage: 0,
      hover: true,
      handleSize: 30,
      onSliderPositionChange: () => {},
      onCursorPositionChange: () => {},
      sliderLineWidth: 1,
      sliderPositionPercentage: 0.5,
      sliderLineColor: 'ffffff',
      vertical: false,
      zoom: 4,
   });

   const emit = defineEmits<{
      (e: 'slideStart', postion: number): void;
      (e: 'slideEnd', postion: number): void;
      (e: 'isSliding', state: boolean): void;
   }>();

   const {
      cursorXPercentage,
      cursorYPercentage,
      hover,
      handle,
      handleSize,
      leftImage,
      onSliderPositionChange,
      onCursorPositionChange,
      rightImage,
      sliderLineColor,
      sliderLineWidth,
      sliderPositionPercentage,
      vertical,
   } = toRefs(props);

   const componentId = Math.random().toString(36).substring(2, 9);
   const horizontal = !vertical.value;
   const containerRef = ref();
   const leftImageRef = ref<HTMLImageElement | null>(null);
   const rightImageRef = ref<HTMLImageElement | null>(null);
   const cursorXPosition = ref(cursorXPercentage.value);
   const cursorYPosition = ref(cursorYPercentage.value);
   const sliderPosition = ref(sliderPositionPercentage.value);
   const containerWidth = ref(0);
   const containerHeight = ref(0);
   const isSliding = ref(false);

   const leftImageClip = computed(() => 1 - sliderPosition.value);
   const rightImageClip = computed(() => sliderPosition.value);

   const containerStyle = computed((): CSSProperties => {
      return {
         height: `${containerHeight.value}px`,
      };
   });

   const leftImageStyle = computed((): CSSProperties => {
      return {
         clipPath: horizontal
            ? `inset(0px ${
                 containerWidth.value * leftImageClip.value
              }px 0px 0px)`
            : `inset(0px 0px ${
                 containerHeight.value * leftImageClip.value
              }px 0px)`,
      };
   });

   const zoomLeftImageStyle = computed((): CSSProperties => {
      return {
         backgroundImage: `url(${leftImage.value})`,
         backgroundSize: `${leftImageRef.value?.naturalWidth}px ${leftImageRef.value?.naturalHeight}px`,
         backgroundPosition: `${cursorXPosition.value * 100}% ${
            cursorYPosition.value * 100
         }%`,
      };
   });

   const zoomRightImageStyle = computed((): CSSProperties => {
      return {
         backgroundImage: `url(${rightImage.value})`,
         backgroundSize: `${rightImageRef.value?.naturalWidth}px ${rightImageRef.value?.naturalHeight}px`,
         backgroundPosition: `${cursorXPosition.value * 100}% ${
            cursorYPosition.value * 100
         }%`,
      };
   });

   const rightImageStyle = computed((): CSSProperties => {
      return {
         clipPath: horizontal
            ? `inset(0px 0px 0px ${
                 containerWidth.value * rightImageClip.value
              }px)`
            : `inset(${
                 containerHeight.value * rightImageClip.value
              }px 0px 0px 0px)`,
      };
   });

   const sliderStyle = computed((): CSSProperties => {
      return {
         flexDirection: horizontal ? 'column' : 'row',
         height: horizontal ? '100%' : `${handleSize.value}px`,
         left: horizontal
            ? `${
                 containerWidth.value * sliderPosition.value -
                 handleSize.value / 2
              }px`
            : '0',
         top: horizontal
            ? '0'
            : `${
                 containerHeight.value * sliderPosition.value -
                 handleSize.value / 2
              }px`,
         width: horizontal ? `${handleSize.value}px` : '100%',
      };
   });

   const lineStyle = computed((): CSSProperties => {
      return {
         background: sliderLineColor.value,
         height: horizontal ? '100%' : `${sliderLineWidth.value}px`,
         width: horizontal ? `${sliderLineWidth.value}px` : '100%',
      };
   });

   const handleDefaultStyle = computed((): CSSProperties => {
      return {
         border: `${sliderLineWidth.value}px solid ${sliderLineColor.value}`,
         height: `${handleSize.value}px`,
         width: `${handleSize.value}px`,
         transform: horizontal ? 'none' : 'rotate(90deg)',
         top: `${
            containerHeight.value * cursorYPosition.value - handleSize.value / 2
         }px`,
      };
   });

   const handleSliding = (event: MouseEvent | TouchEvent | KeyboardEvent) => {
      const e = event as TouchEvent;

      // @ts-expect-error
      const cursorXFromViewport = e.touches ? e.touches[0].pageX : e.pageX;

      //@ts-expect-error
      const cursorYFromViewport = e.touches ? e.touches[0].pageY : e.pageY;

      const cursorXFromWindow = cursorXFromViewport - window.scrollX;
      const cursorYFromWindow = cursorYFromViewport - window.scrollY;
      const imagePosition = rightImageRef.value!.getBoundingClientRect();
      let position = horizontal
         ? cursorXFromWindow - imagePosition.left
         : cursorYFromWindow - imagePosition.top;

      const minPosition = 0 + sliderLineWidth.value / 2;
      const maxPosition = horizontal
         ? containerWidth.value - sliderLineWidth.value / 2
         : containerHeight.value - sliderLineWidth.value / 2;
      if (position < minPosition) {
         position = minPosition;
      }
      if (position > maxPosition) {
         position = maxPosition;
      }

      sliderPosition.value = horizontal
         ? position / containerWidth.value
         : position / containerHeight.value;

      let x = cursorXFromWindow - imagePosition.left;
      let y = cursorYFromWindow - imagePosition.top;

      cursorXPosition.value = x / containerWidth.value;
      cursorYPosition.value = y / containerHeight.value;

      if (onSliderPositionChange.value) {
         onSliderPositionChange.value(
            horizontal
               ? position / containerWidth.value
               : position / containerHeight.value
         );
      }

      if (onCursorPositionChange.value) {
         onCursorPositionChange.value(
            horizontal
               ? position / containerWidth.value
               : position / containerHeight.value,
            horizontal
               ? position / containerWidth.value
               : position / containerHeight.value
         );
      }
   };

   const startSliding = (event: MouseEvent | TouchEvent | KeyboardEvent) => {
      isSliding.value = true;
      emit('slideStart', sliderPosition.value);
      emit('isSliding', isSliding.value);

      if (!horizontal) {
         event.preventDefault();
      } else if (!('touches' in event)) {
         event.preventDefault();
      }

      window.addEventListener('mousemove', handleSliding);
      window.addEventListener('touchmove', handleSliding);
      window.addEventListener('mouseup', handleSliding);
      window.addEventListener('touchend', handleSliding);
   };

   const finishSliding = () => {
      isSliding.value = false;
      emit('slideEnd', sliderPosition.value);
      emit('isSliding', isSliding.value);

      window.removeEventListener('mousemove', handleSliding);
      window.removeEventListener('touchmove', handleSliding);
      window.removeEventListener('mouseup', handleSliding);
      window.removeEventListener('touchend', handleSliding);
   };

   const forceRenderHover = (): void => {
      const instance = getCurrentInstance();
      instance?.proxy?.$forceUpdate();
      const containerElement = containerRef.value;
      if (props.hover) {
         containerElement?.addEventListener('mousemove', startSliding);
         containerElement?.addEventListener('mouseleave', finishSliding);
      } else {
         containerElement?.removeEventListener('mousemove', startSliding);
         containerElement?.removeEventListener('mouseleave', finishSliding);

         containerElement?.addEventListener('mouseup', finishSliding);
         containerElement?.addEventListener('touchend', finishSliding);
      }
   };

   onMounted(() => {
      const containerElement = containerRef.value;
      const resizeObserver = new ResizeObserver(([entry]) => {
         const currentContainerWidth =
            entry.target.getBoundingClientRect().width;
         containerWidth.value = currentContainerWidth;
      });
      resizeObserver.observe(containerElement);

      return () => resizeObserver.disconnect();
   });

   onMounted(() => {
      const containerElement = containerRef.value;
      if (props.hover) {
         containerElement?.addEventListener('mousemove', startSliding);
         containerElement?.addEventListener('mouseleave', finishSliding);
      }
   });

   onBeforeUnmount(() => {
      const containerElement = containerRef.value;

      containerElement?.removeEventListener('mousemove', startSliding);
      containerElement?.removeEventListener('mouseleave', finishSliding);
      window.removeEventListener('mousemove', handleSliding);
      window.removeEventListener('touchmove', handleSliding);
      window.removeEventListener('mouseup', finishSliding);
      window.removeEventListener('touchend', finishSliding);
   });

   watch(hover, () => {
      forceRenderHover();
   });

   watch([() => containerWidth.value], () => {
      const leftImageWidthHeightRatio =
         leftImageRef.value!.naturalHeight / leftImageRef.value!.naturalWidth;
      const rightImageWidthHeightRatio =
         rightImageRef.value!.naturalHeight / rightImageRef.value!.naturalWidth;

      const idealWidthHeightRatio = Math.min(
         leftImageWidthHeightRatio,
         rightImageWidthHeightRatio
      );

      const idealContainerHeight = containerWidth.value * idealWidthHeightRatio;
      containerHeight.value = idealContainerHeight;
   });
</script>
