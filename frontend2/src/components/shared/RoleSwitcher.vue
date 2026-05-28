<script setup>
  import { appTemplate } from '@/config/appTemplate';
  import { useAppStore } from '@/stores/useAppStore';

  const appStore = useAppStore();
</script>

<template>
  <aside class="role-switcher">
    <p class="role-switcher__label">Cambiar rol</p>
    <div class="role-switcher__items">
      <button
        v-for="item in appTemplate.roleSwitcher"
        :key="item.key"
        type="button"
        class="role-chip"
        :class="{ 'role-chip--active': appStore.role === item.key }"
        :style="
          appStore.role === item.key
            ? { background: appTemplate.roles[item.key].accent }
            : undefined
        "
        @click="appStore.setRole(item.key, item.userId || undefined)"
      >
        {{ item.label }}
      </button>
    </div>
  </aside>
</template>
