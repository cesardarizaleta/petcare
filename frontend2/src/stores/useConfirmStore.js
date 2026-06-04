import { defineStore } from 'pinia';

export const useConfirmStore = defineStore('confirm', {
  state: () => ({
    isOpen: false,
    title: '¿Confirmar acción?',
    message: '¿Estás seguro de que deseas realizar esta acción?',
    confirmText: 'Confirmar',
    cancelText: 'Cancelar',
    type: 'warning', // 'danger' | 'warning' | 'info' | 'success'
    resolve: null,
  }),
  actions: {
    confirm({
      title = '¿Confirmar acción?',
      message = '¿Estás seguro de que deseas realizar esta acción?',
      confirmText = 'Confirmar',
      cancelText = 'Cancelar',
      type = 'warning',
    } = {}) {
      this.isOpen = true;
      this.title = title;
      this.message = message;
      this.confirmText = confirmText;
      this.cancelText = cancelText;
      this.type = type;

      return new Promise((resolve) => {
        this.resolve = resolve;
      });
    },
    handleConfirm() {
      if (this.resolve) {
        this.resolve(true);
      }
      this.isOpen = false;
      this.resolve = null;
    },
    handleCancel() {
      if (this.resolve) {
        this.resolve(false);
      }
      this.isOpen = false;
      this.resolve = null;
    },
  },
});
