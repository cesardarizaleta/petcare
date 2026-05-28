<script setup>
  import { computed } from 'vue';
  import { useRoute, useRouter, RouterLink } from 'vue-router';
  import { appTemplate } from '@/config/appTemplate';
  import { useAppStore } from '@/stores/useAppStore';
  import Logo from '@/components/shared/Logo.vue';
  import AppIcon from '@/components/shared/AppIcon.vue';
  import NotificationsPanel from '@/components/shared/NotificationsPanel.vue';

  const appStore = useAppStore();
  const route = useRoute();
  const router = useRouter();

  const navigation = computed(() => appTemplate.navigation[appStore.role]);

  const handleLogout = () => {
    appStore.logout();
    router.push('/login');
  };
</script>

<template>
  <aside class="sidebar">
    <div class="sidebar__brand">
      <Logo />
    </div>

    <div class="sidebar__module">
      <p class="sidebar__label">Módulo</p>
      <p class="sidebar__module-name">{{ appTemplate.roles[appStore.role].label }}</p>
    </div>

    <nav class="sidebar__nav" aria-label="Navegación principal">
      <RouterLink
        v-for="item in navigation"
        :key="item.to"
        :to="item.to"
        class="sidebar__link"
        :class="{ 'sidebar__link--active': route.path.startsWith(item.to) }"
      >
        <span class="sidebar__icon" aria-hidden="true"
          ><AppIcon :name="item.icon" :size="16"
        /></span>
        <span>{{ item.label }}</span>
      </RouterLink>
    </nav>

    <div class="sidebar__footer" style="display: flex; align-items: center; justify-content: space-between;">
      <span>{{ appTemplate.footerLabel }}</span>
      <div style="display: flex; gap: 12px; align-items: center;">
        <NotificationsPanel />
        <button @click="handleLogout" title="Cerrar sesión" style="background: transparent; border: none; cursor: pointer; color: var(--color-text-light); display: flex; align-items: center;">
          <AppIcon name="log-out" :size="20" />
        </button>
      </div>
    </div>
  </aside>
</template>
