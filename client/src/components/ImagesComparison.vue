<template>
   <div class="image-comparison">
      <div class="image-wrapper">
         <img
            :src="image1"
            alt="Image 1"
            class="image"
         />
         <div
            class="image-overlay"
            :style="{ width: `${sliderPosition}%` }"
         >
            <img
               :src="image2"
               alt="Image 2"
               class="image"
            />
         </div>
         <div
            class="slider"
            @mousemove="updateSliderPosition"
            @mouseleave="resetSliderPosition"
            @click="setSliderPosition"
         ></div>
      </div>
   </div>
</template>

<script setup lang="ts">
   import { ref } from 'vue';

   const image1 =
      'https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Cat03.jpg/800px-Cat03.jpg'; // Đường dẫn tới ảnh 1
   const image2 =
      'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRDCsqRYLAFDdL4Ix_AHai7kNVyoPV9Ssv1xg&s'; // Đường dẫn tới ảnh 2

   const sliderPosition = ref(50); // Vị trí ban đầu của thanh trượt

   const updateSliderPosition = (event) => {
      const rect = event.currentTarget.getBoundingClientRect();
      const offsetX = event.clientX - rect.left; // Tính toán vị trí chuột
      sliderPosition.value = (offsetX / rect.width) * 100; // Cập nhật vị trí thanh trượt
   };

   const resetSliderPosition = () => {
      // Có thể reset thanh trượt nếu cần
   };

   const setSliderPosition = (event) => {
      const rect = event.currentTarget.getBoundingClientRect();
      const offsetX = event.clientX - rect.left; // Tính toán vị trí chuột
      sliderPosition.value = (offsetX / rect.width) * 100; // Cập nhật vị trí thanh trượt khi click
   };
</script>

<style scoped>
   .image-comparison {
      position: relative;
      width: 100%;
      max-width: 600px; /* Chiều rộng tối đa của component */
      overflow: hidden;
   }

   .image-wrapper {
      position: relative;
      width: 100%;
   }

   .image {
      width: 100%;
      display: block;
   }

   .image-overlay {
      position: absolute;
      top: 0;
      left: 0;
      height: 100%;
      overflow: hidden;
      transition: width 0.3s ease; /* Hiệu ứng chuyển động khi thay đổi vị trí thanh trượt */
   }

   .slider {
      position: absolute;
      top: 0;
      left: 0;
      height: 100%;
      cursor: ew-resize; /* Thay đổi con trỏ khi hover */
   }
</style>
