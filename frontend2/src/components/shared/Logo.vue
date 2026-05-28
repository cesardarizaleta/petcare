<script setup>
  import AppIcon from './AppIcon.vue';

  defineProps({
    size: {
      type: String,
      default: 'md',
    },
    showText: {
      type: Boolean,
      default: true,
    },
  });
</script>

<template>
  <div class="brand" :class="`brand--${size}`">
    <img src="/logo.png" alt="Logo" class="brand__mark" style="background: transparent; box-shadow: none;" />
    <div v-if="showText" class="brand__wordmark">
      <span class="brand__wordmark-main">Pet</span>
      <span class="brand__wordmark-accent">Care</span>
    </div>
  </div>
</template>
