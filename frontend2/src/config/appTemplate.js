export const appTemplate = {
  name: 'PetCare',
  footerLabel: 'PetCare v1.0',
  roles: {
    owner: { label: 'Portal Propietario', accent: '#C2A769', light: '#F7F1E6' },
    receptionist: { label: 'Recepción', accent: '#A5BA8E', light: '#F3F6F0' },
    vet: { label: 'Veterinario', accent: '#7D6430', light: '#F7F1E6' },
    technician: { label: 'Técnico Veterinario', accent: '#7da84e', light: '#F3F6F0' },
    manager: { label: 'Gerente', accent: '#7aa250', light: '#F7F1E6' },
  },
  navigation: {
    owner: [
      { to: '/portal/dashboard', icon: 'house', label: 'Inicio' },
      { to: '/portal/appointments', icon: 'calendar-days', label: 'Mis Citas' },
      { to: '/portal/schedule', icon: 'calendar-plus', label: 'Agendar Cita' },
      { to: '/portal/pets', icon: 'paw-print', label: 'Mis Mascotas' },
      { to: '/portal/history', icon: 'clock-3', label: 'Historial' },
      { to: '/portal/profile', icon: 'user-round', label: 'Mi Perfil' },
    ],
    receptionist: [
      { to: '/reception/dashboard', icon: 'layout-dashboard', label: 'Dashboard' },
      { to: '/reception/calendar', icon: 'calendar-days', label: 'Calendario' },
      { to: '/reception/new-appointment', icon: 'notebook-pen', label: 'Nueva Cita' },
      { to: '/reception/checkin', icon: 'clipboard-check', label: 'Check-in' },
      { to: '/reception/waitlist', icon: 'hourglass', label: 'Lista de Espera' },
      { to: '/reception/owners', icon: 'search', label: 'Propietarios' },
    ],
    vet: [
      { to: '/vet/dashboard', icon: 'stethoscope', label: 'Mi Agenda' },
      { to: '/vet/patients', icon: 'dog', label: 'Pacientes del Día' },
      { to: '/vet/records', icon: 'clipboard-list', label: 'Fichas Clínicas' },
      { to: '/vet/consultations', icon: 'clipboard-pen-line', label: 'Registrar Consulta' },
      { to: '/vet/vaccines', icon: 'syringe', label: 'Vacunas' },
      { to: '/vet/dewormings', icon: 'worm', label: 'Desparasitaciones' },
    ],
    technician: [
      { to: '/technician/inventory', icon: 'clipboard-list', label: 'Catálogo de Insumos' },
      { to: '/technician/register-supply', icon: 'clipboard-pen-line', label: 'Registrar Insumos' },
      { to: '/technician/reposition', icon: 'notebook-pen', label: 'Reposicion de Stock' },
      {
        to: '/technician/supply-requisition',
        icon: 'clipboard-check',
        label: 'Solicitud de Reabastecimiento',
      },
      { to: '/technician/tracking', icon: 'calendar-plus', label: 'Seguimiento de Solicitudes' },
    ],
    manager: [
      { to: '/manager/requests', icon: 'clipboard-check', label: 'Solicitudes del Gerente' },
      { to: '/manager/dashboard', icon: 'layout-dashboard', label: 'Tablero Gerencial' },
    ],
  },
  roleSwitcher: [
    { key: 'owner', label: 'Propietario', userId: 'o1' },
    { key: 'receptionist', label: 'Recepcionista', userId: '' },
    { key: 'vet', label: 'Veterinario', userId: 'v1' },
    { key: 'technician', label: 'Técnico Veterinario', userId: '' },
    { key: 'manager', label: 'Gerente', userId: '' },
  ],
};
