<template>
  <!-- 
    <RouterView /> es un componente especial donde Vue inyectará la página 
    correspondiente a la URL en la que estemos navegando.
  -->
  <RouterView />
  
  <!-- 
    ToastHost se encarga de mostrar pequeñas alertas y notificaciones globales
    (burbujas emergentes) sin importar en qué vista estemos.
  -->
  <ToastHost />
</template>

<script setup>
  import { RouterView } from 'vue-router';
  import ToastHost from '@/components/ui/ToastHost.vue';
</script>
