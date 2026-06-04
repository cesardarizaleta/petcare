<script setup>
import { ref, onMounted } from 'vue';
import PageHeader from '@/components/shared/PageHeader.vue';
import DashboardCard from '@/components/shared/DashboardCard.vue';
import http from '@/lib/http';
import { useToastStore } from '@/stores/useToastStore';
import AppIcon from '@/components/shared/AppIcon.vue';

const toastStore = useToastStore();

const users = ref([]);
const loading = ref(false);
const submitting = ref(false);

// Form States
const isEditing = ref(false);
const selectedUserId = ref(null);
const form = ref({
  email: '',
  first_name: '',
  last_name: '',
  password: '',
  roles: [],
  is_active: true,
  dni: '',
  phone: '',
  address: '',
  specialty: ''
});

const ROLE_OPTIONS = [
  { value: 'owner', label: 'Propietario' },
  { value: 'receptionist', label: 'Recepcionista' },
  { value: 'veterinarian', label: 'Veterinario' },
  { value: 'technician', label: 'Técnico Veterinario' },
  { value: 'manager', label: 'Gerente' },
  { value: 'superadmin', label: 'Super Administrador' }
];

onMounted(async () => {
  await fetchUsers();
});

const fetchUsers = async () => {
  loading.value = true;
  try {
    const res = await http.get('/api/v1/auth/superadmin/users/');
    users.value = res.data;
  } catch (err) {
    console.error('Error fetching users:', err);
    toastStore.push({
      title: 'Error al cargar usuarios',
      description: 'No se pudieron recuperar los usuarios del servidor.',
      type: 'error'
    });
  } finally {
    loading.value = false;
  }
};

const resetForm = () => {
  form.value = {
    email: '',
    first_name: '',
    last_name: '',
    password: '',
    roles: [],
    is_active: true,
    dni: '',
    phone: '',
    address: '',
    specialty: ''
  };
  isEditing.value = false;
  selectedUserId.value = null;
};

const handleEdit = (user) => {
  isEditing.value = true;
  selectedUserId.value = user.id;
  form.value = {
    email: user.email,
    first_name: user.first_name,
    last_name: user.last_name,
    password: '', // Leave blank unless changing
    roles: [...user.roles],
    is_active: user.is_active,
    dni: user.dni || '',
    phone: user.phone || '',
    address: user.address || '',
    specialty: user.specialty || ''
  };
};

const handleSubmit = async () => {
  // Simple validation
  if (!form.value.email || !form.value.first_name || !form.value.last_name) {
    toastStore.push({
      title: 'Campos incompletos',
      description: 'Nombre, apellido y correo electrónico son requeridos.',
      type: 'error'
    });
    return;
  }

  if (!isEditing.value && !form.value.password) {
    toastStore.push({
      title: 'Contraseña requerida',
      description: 'Debe ingresar una contraseña para nuevos usuarios.',
      type: 'error'
    });
    return;
  }

  // DNI pattern validation (6-10 digits) if provided
  if (form.value.dni) {
    const dniStr = String(form.value.dni).trim();
    if (!/^\d{6,10}$/.test(dniStr)) {
      toastStore.push({
        title: 'Formato de DNI inválido',
        description: 'La cédula/DNI debe contener entre 6 y 10 dígitos positivos.',
        type: 'error'
      });
      return;
    }
  }

  // Phone pattern validation if provided
  if (form.value.phone) {
    const phoneStr = String(form.value.phone).trim();
    if (!/^\+?[\d\s\-()]{7,20}$/.test(phoneStr)) {
      toastStore.push({
        title: 'Formato de teléfono inválido',
        description: 'El teléfono debe tener un formato válido (entre 7 y 20 caracteres).',
        type: 'error'
      });
      return;
    }
  }

  submitting.value = true;
  try {
    if (isEditing.value) {
      // Update
      const payload = {
        first_name: form.value.first_name,
        last_name: form.value.last_name,
        roles: form.value.roles,
        is_active: form.value.is_active,
        dni: form.value.dni,
        phone: form.value.phone,
        address: form.value.address,
        specialty: form.value.roles.includes('veterinarian') ? form.value.specialty : ''
      };
      if (form.value.password) {
        payload.password = form.value.password;
      }
      await http.put(`/api/v1/auth/superadmin/users/${selectedUserId.value}/`, payload);
      toastStore.push({
        title: 'Usuario actualizado',
        description: 'Los datos del usuario han sido modificados con éxito.',
        type: 'success'
      });
    } else {
      // Create
      const payload = {
        email: form.value.email,
        first_name: form.value.first_name,
        last_name: form.value.last_name,
        password: form.value.password,
        roles: form.value.roles,
        dni: form.value.dni,
        phone: form.value.phone,
        address: form.value.address,
        specialty: form.value.roles.includes('veterinarian') ? form.value.specialty : ''
      };
      await http.post('/api/v1/auth/superadmin/users/', payload);
      toastStore.push({
        title: 'Usuario registrado',
        description: `El usuario ${form.value.email} fue creado exitosamente.`,
        type: 'success'
      });
    }
    resetForm();
    await fetchUsers();
  } catch (err) {
    console.error('Error submitting form:', err);
    const detail = err.response?.data?.error || 'Ocurrió un error en el servidor.';
    toastStore.push({
      title: 'Error de registro',
      description: detail,
      type: 'error'
    });
  } finally {
    submitting.value = false;
  }
};

const handleDeactivate = async (userId) => {
  if (!confirm('¿Está seguro de que desea desactivar este usuario? El usuario ya no podrá iniciar sesión.')) {
    return;
  }

  try {
    await http.delete(`/api/v1/auth/superadmin/users/${userId}/`);
    toastStore.push({
      title: 'Usuario desactivado',
      description: 'El estado del usuario ha sido cambiado a inactivo.',
      type: 'success'
    });
    await fetchUsers();
  } catch (err) {
    console.error('Error deactivating user:', err);
    toastStore.push({
      title: 'Error al desactivar',
      description: 'No se pudo completar la operación en el servidor.',
      type: 'error'
    });
  }
};

const getRoleBadgeClass = (role) => {
  const map = {
    superadmin: 'role-badge--superadmin',
    manager: 'role-badge--manager',
    veterinarian: 'role-badge--vet',
    vet: 'role-badge--vet',
    receptionist: 'role-badge--receptionist',
    technician: 'role-badge--technician',
    owner: 'role-badge--owner'
  };
  return map[role] || 'role-badge--default';
};

const getRoleLabel = (role) => {
  const map = {
    superadmin: 'SuperAdmin',
    manager: 'Gerente',
    veterinarian: 'Veterinario',
    vet: 'Veterinario',
    receptionist: 'Recepcionista',
    technician: 'Técnico',
    owner: 'Propietario'
  };
  return map[role] || role;
};
</script>

<template>
  <div class="superadmin-layout">
    <PageHeader
      title="Super Administración"
      subtitle="Control central de usuarios, asignación de roles y estados de acceso."
    />

    <div class="dashboard-grid">
      <!-- Left Column: User Directory -->
      <div class="left-col">
        <DashboardCard title="Directorio de Usuarios" icon="users">
          <div v-if="loading" class="loading-state">
            <span class="spinner"></span>
            <p>Cargando directorio de usuarios...</p>
          </div>
          
          <div v-else class="table-wrap">
            <table class="table">
              <thead>
                <tr>
                  <th>Usuario / Email</th>
                  <th>Nombre Completo</th>
                  <th>Roles Asignados</th>
                  <th>Contacto</th>
                  <th>Especialidad</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="user in users" :key="user.id" class="table__row" :class="{ 'row--inactive': !user.is_active }">
                  <td class="user-email-cell">
                    <span class="user-email">{{ user.email }}</span>
                  </td>
                  <td>{{ user.first_name }} {{ user.last_name }}</td>
                  <td>
                    <div class="roles-container">
                      <span
                        v-for="role in user.roles"
                        :key="role"
                        class="role-badge"
                        :class="getRoleBadgeClass(role)"
                      >
                        {{ getRoleLabel(role) }}
                      </span>
                      <span v-if="!user.roles || user.roles.length === 0" class="role-badge role-badge--none">
                        Sin Rol
                      </span>
                    </div>
                  </td>
                  <td>
                    <div class="contact-details" v-if="user.dni || user.phone || user.address">
                      <div v-if="user.dni" class="contact-item"><span class="label">DNI:</span> {{ user.dni }}</div>
                      <div v-if="user.phone" class="contact-item"><span class="label">Tel:</span> {{ user.phone }}</div>
                      <div v-if="user.address" class="contact-item contact-item--address" :title="user.address"><span class="label">Dir:</span> {{ user.address }}</div>
                    </div>
                    <span v-else class="text-muted text-xs">—</span>
                  </td>
                  <td>
                    <span v-if="user.specialty" class="specialty-text">{{ user.specialty }}</span>
                    <span v-else class="text-muted text-xs">—</span>
                  </td>
                  <td>
                    <span class="status-indicator" :class="user.is_active ? 'status-indicator--active' : 'status-indicator--inactive'">
                      <span class="status-dot"></span>
                      {{ user.is_active ? 'Activo' : 'Inactivo' }}
                    </span>
                  </td>
                  <td>
                    <div class="action-buttons">
                      <button
                        class="btn btn--secondary btn--sm"
                        title="Editar usuario"
                        @click="handleEdit(user)"
                      >
                        Editar
                      </button>
                      <button
                        v-if="user.is_active"
                        class="btn btn--danger btn--sm"
                        title="Desactivar acceso"
                        @click="handleDeactivate(user.id)"
                      >
                        Desactivar
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </DashboardCard>
      </div>

      <!-- Right Column: User Management Form -->
      <div class="right-col">
        <DashboardCard :title="isEditing ? 'Editar Usuario' : 'Registrar Nuevo Usuario'" icon="user-round-plus">
          <form class="stack form-container" @submit.prevent="handleSubmit">
            <div class="field">
              <label for="email">Correo Electrónico*</label>
              <input
                id="email"
                type="email"
                class="input"
                v-model="form.email"
                required
                :disabled="isEditing"
                placeholder="usuario@petcare.com"
              />
            </div>

            <div class="field">
              <label for="first_name">Nombre*</label>
              <input
                id="first_name"
                type="text"
                class="input"
                v-model="form.first_name"
                required
                placeholder="Nombre"
              />
            </div>

            <div class="field">
              <label for="last_name">Apellido*</label>
              <input
                id="last_name"
                type="text"
                class="input"
                v-model="form.last_name"
                required
                placeholder="Apellido"
              />
            </div>

            <div class="field">
              <label for="password">
                {{ isEditing ? 'Nueva Contraseña (Dejar vacío para mantener)' : 'Contraseña*' }}
              </label>
              <input
                id="password"
                type="password"
                class="input"
                v-model="form.password"
                :required="!isEditing"
                placeholder="Contraseña"
              />
            </div>

            <div class="field">
              <label for="dni">DNI / Cédula</label>
              <input
                id="dni"
                type="text"
                class="input"
                v-model="form.dni"
                placeholder="Ej. 12345678 (6 a 10 dígitos)"
              />
            </div>

            <div class="field">
              <label for="phone">Teléfono</label>
              <input
                id="phone"
                type="tel"
                class="input"
                v-model="form.phone"
                placeholder="Ej. +541155554444"
              />
            </div>

            <div class="field">
              <label for="address">Dirección</label>
              <input
                id="address"
                type="text"
                class="input"
                v-model="form.address"
                placeholder="Calle, Ciudad, Provincia"
              />
            </div>

            <div v-if="form.roles.includes('veterinarian')" class="field">
              <label for="specialty">Especialidad Veterinaria</label>
              <input
                id="specialty"
                type="text"
                class="input"
                v-model="form.specialty"
                placeholder="Ej. Cirugía, Fisioterapia, etc."
              />
            </div>

            <div class="field">
              <label>Roles de Usuario</label>
              <div class="roles-checkboxes-grid">
                <label v-for="opt in ROLE_OPTIONS" :key="opt.value" class="checkbox-label">
                  <input
                    type="checkbox"
                    :value="opt.value"
                    v-model="form.roles"
                    class="checkbox-input"
                  />
                  <span>{{ opt.label }}</span>
                </label>
              </div>
            </div>

            <div v-if="isEditing" class="field">
              <label class="checkbox-label toggle-label">
                <input
                  type="checkbox"
                  v-model="form.is_active"
                  class="checkbox-input"
                />
                <span>Usuario Activo (Permitir Ingreso)</span>
              </label>
            </div>

            <div class="form-actions">
              <button
                v-if="isEditing"
                type="button"
                class="btn btn--secondary"
                @click="resetForm"
              >
                Cancelar
              </button>
              <button
                type="submit"
                class="btn btn--primary"
                :disabled="submitting"
              >
                {{ submitting ? 'Guardando...' : (isEditing ? 'Actualizar Usuario' : 'Registrar Usuario') }}
              </button>
            </div>
          </form>
        </DashboardCard>
      </div>
    </div>
  </div>
</template>

<style scoped>
.superadmin-layout {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 1.5rem;
  align-items: start;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 40px;
  color: rgba(61, 61, 61, 0.6);
}

.spinner {
  width: 24px;
  height: 24px;
  border: 3px solid rgba(0, 0, 0, 0.1);
  border-top-color: var(--brand-strong);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.row--inactive {
  opacity: 0.65;
  background-color: var(--surface-soft);
}

.user-email-cell {
  font-weight: 600;
  color: var(--text-strong);
}

.roles-container {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.role-badge {
  font-size: 0.725rem;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: 9999px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.role-badge--superadmin { background-color: #EBDEF0; color: #7D3C98; }
.role-badge--manager { background-color: #D4EFDF; color: #196F3D; }
.role-badge--vet { background-color: #FCF3CF; color: #B7950B; }
.role-badge--receptionist { background-color: #D5F5E3; color: #117A65; }
.role-badge--technician { background-color: #D6EAF8; color: #2E86C1; }
.role-badge--owner { background-color: #E5E7E9; color: #5D6D7E; }
.role-badge--none { background-color: #FADBD8; color: #CB4335; }

.status-indicator {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.85rem;
  font-weight: 500;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-indicator--active {
  color: #27ae60;
}
.status-indicator--active .status-dot {
  background-color: #27ae60;
  box-shadow: 0 0 8px rgba(39, 174, 96, 0.4);
}

.status-indicator--inactive {
  color: #c0392b;
}
.status-indicator--inactive .status-dot {
  background-color: #c0392b;
}

.action-buttons {
  display: flex;
  gap: 6px;
}

.btn--sm {
  padding: 4px 8px;
  font-size: 0.75rem;
}

.btn--danger {
  background-color: rgba(192, 57, 43, 0.1);
  color: #c0392b;
  border: 1px solid rgba(192, 57, 43, 0.2);
}
.btn--danger:hover {
  background-color: #c0392b;
  color: white;
}

.form-container {
  gap: 16px;
}

.roles-checkboxes-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-top: 8px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.875rem;
  cursor: pointer;
}

.checkbox-input {
  width: 16px;
  height: 16px;
  border-radius: 4px;
  border: 1px solid var(--border);
  accent-color: var(--brand-strong);
}

.toggle-label {
  padding: 8px 12px;
  background-color: var(--surface-soft);
  border-radius: var(--radius-md);
  border: 1px solid var(--border);
  margin-top: 6px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 10px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 1024px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
}

.contact-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-size: 0.775rem;
  color: var(--text-normal);
}

.contact-item {
  white-space: nowrap;
}

.contact-item--address {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 140px;
}

.contact-item .label {
  font-weight: 600;
  color: var(--text-muted);
}

.specialty-text {
  font-size: 0.825rem;
  font-weight: 600;
  color: var(--brand-strong);
}

.text-muted {
  color: var(--text-muted);
}

.text-xs {
  font-size: 0.75rem;
}
</style>
