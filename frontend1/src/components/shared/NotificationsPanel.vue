<script setup>
import { computed, ref } from 'vue';
import { useAppStore } from '@/stores/useAppStore';
import AppIcon from '@/components/shared/AppIcon.vue';

const appStore = useAppStore();
const isOpen = ref(false);

const notifications = computed(() => appStore.notifications);
const unreadCount = computed(() => notifications.value.filter(n => !n.read).length);

function toggle() {
  isOpen.value = !isOpen.value;
}

function markAsRead(id) {
  appStore.markNotificationAsRead(id);
}
</script>

<template>
  <div class="notifications">
    <button class="btn btn--ghost notifications__btn notifications__btn--trigger" @click="toggle">
      <AppIcon name="bell" :size="20" />
      <span v-if="unreadCount > 0" class="notifications__badge">{{ unreadCount }}</span>
    </button>
    
    <div v-if="isOpen" class="notifications__dropdown card notifications__dropdown-panel">
      <div class="toolbar notifications__toolbar">
        <h3 class="notifications__header">Notificaciones</h3>
        <button class="icon-btn" @click="toggle" aria-label="Cerrar">
          <AppIcon name="x" :size="16" />
        </button>
      </div>
      <div v-if="notifications.length === 0" class="notifications__empty">
        No tienes notificaciones
      </div>
      <div v-else class="notifications__list">
        <div v-for="notif in notifications" :key="notif.id" 
             class="notifications__item"
             :style="{ opacity: notif.read ? 0.6 : 1 }">
          <p class="notifications__item-title">{{ notif.title }}</p>
          <p class="notifications__item-message">{{ notif.description }}</p>
          <button v-if="!notif.read" @click="markAsRead(notif.id)" class="icon-btn notifications__item-read-btn" aria-label="Marcar como leída">
            <AppIcon name="check" :size="14" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.notifications__btn--trigger {
  position: relative;
  padding: 8px;
}

.notifications__dropdown-panel {
  position: absolute;
  bottom: 60px;
  left: 16px;
  width: 300px;
  z-index: 100;
  max-height: 400px;
  overflow-y: auto;
}

.notifications__toolbar {
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.notifications__header {
  font-size: 14px;
  margin: 0;
  font-weight: 600;
  color: var(--text-strong);
}

.notifications__empty {
  text-align: center;
  padding: 20px;
  color: var(--text-muted, rgba(61, 61, 61, 0.68));
  font-size: 13px;
}

.notifications__list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.notifications__item {
  padding: 12px;
  border-radius: 6px;
  background: var(--surface-soft);
  font-size: 13px;
  position: relative;
}

.notifications__item-title {
  font-weight: 600;
  margin: 0 0 4px;
  padding-right: 28px;
  color: var(--text-strong);
}

.notifications__item-message {
  margin: 0;
  color: var(--text);
  line-height: 1.4;
}

.notifications__item-read-btn {
  position: absolute;
  top: 8px;
  right: 8px;
}

.notifications__badge {
  position: absolute;
  top: 0;
  right: 0;
  background: var(--danger);
  color: white;
  border-radius: 50%;
  width: 18px;
  height: 18px;
  font-size: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}

.icon-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 6px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: var(--text);
  transition: background 0.2s, color 0.2s;
}

.icon-btn:hover {
  background: rgba(194, 167, 105, 0.12);
  color: var(--brand-strong);
}
</style>
