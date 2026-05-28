import { defineStore } from 'pinia';

let toastId = 0;

export const useToastStore = defineStore('toast', {
  state: () => ({
    items: [],
  }),
  actions: {
    push({ title, description = '', type = 'info' }) {
      const id = ++toastId;
      this.items.push({ id, title, description, type });

      window.setTimeout(() => {
        this.remove(id);
      }, 3600);
    },
    remove(id) {
      this.items = this.items.filter((item) => item.id !== id);
    },
  },
});
