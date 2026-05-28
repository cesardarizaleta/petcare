<script setup>
  import { appTemplate } from '@/config/appTemplate';
  import { useAppStore } from '@/stores/useAppStore';
  import { useRouter } from 'vue-router';
  import { switchRole as switchRoleAction } from '@/lib/petcare';

  const appStore = useAppStore();
  const router = useRouter();

  function switchRole(item) {
    switchRoleAction(item, appStore, router);
  }

  function logout() {
    appStore.logout();
    router.push('/login');
  }
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
        @click="switchRole(item)"
      >
        {{ item.label }}
      </button>

      <button
        type="button"
        class="role-chip"
        style="background: rgba(178, 60, 60, 0.12); color: var(--danger); border-color: rgba(178, 60, 60, 0.2);"
        @click="logout"
      >
        Cerrar sesión
      </button>
    </div>
  </aside>
</template>
