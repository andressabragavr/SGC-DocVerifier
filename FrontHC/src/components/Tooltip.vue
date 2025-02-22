<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent ({
    name: 'Tooltip',
    setup() {
      const isActive = ref(false);
      const showTooltip = () => {
        isActive.value = true;
      };
      const hideTooltip = () => {
        isActive.value = false;
      };
      return {
        isActive,
        showTooltip,
        hideTooltip,
      };
    },
});
</script>

<template>
    <div class="tooltip-container" @mouseover="showTooltip" @mouseout="hideTooltip">
        <slot></slot> 
        <div v-if="isActive" class="tooltip-text"> 
            <slot name="tooltip"></slot> 
        </div> 
    </div>
</template>

<style scoped>
.tooltip-container { 
    position: relative; 
    display: inline-block; 
    cursor: pointer; 
} 

.tooltip-text { 
    visibility: visible; 
    width: 200px; 
    background-color: #555; 
    color: #fff; 
    text-align: center; 
    border-radius: 5px; 
    padding: 10px; 
    position: absolute; 
    z-index: 1; 
    top: 50%; 
    left: 100%; 
    transform: translateY(-50%); 
    opacity: 1; 
    transition: opacity 0.3s; 
    margin-top: 10px;
}

.tooltip-container .tooltip-text::after { 
    content: ''; 
    position: absolute; 
    top: 50%; 
    left: 100%; 
    transform: translateY(-50%); 
    border-width: 5px; 
    border-style: solid; 
    border-color: #555 transparent transparent transparent; 
}
</style>