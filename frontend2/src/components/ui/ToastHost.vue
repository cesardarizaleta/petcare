<script setup>
  import { storeToRefs } from 'pinia';
  import { useToastStore } from '@/stores/useToastStore';

  const toastStore = useToastStore();
  const { items } = storeToRefs(toastStore);
</script>

<template>
  <div class="toast-stack" aria-live="polite" aria-atomic="true">
    <TransitionGroup name="toast" tag="div" class="toast-stack__group">
      <article
        v-for="toast in items"
        :key="toast.id"
        class="toast"
        :class="`toast--${toast.type}`"
        @click="toastStore.remove(toast.id)"
      >
        <p class="toast__title">{{ toast.title }}</p>
        <p v-if="toast.description" class="toast__description">{{ toast.description }}</p>
      </article>
    </TransitionGroup>
  </div>
</template>
