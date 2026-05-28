export const appTemplate = {
  name: 'PetCare',
  footerLabel: 'PetCare v1.0',
  roles: {
    owner: { label: 'Portal Propietario', accent: '#C2A769', light: '#F7F1E6' },
    receptionist: { label: 'Recepción', accent: '#A5BA8E', light: '#F3F6F0' },
    vet: { label: 'Veterinario', accent: '#7D6430', light: '#F7F1E6' },
  },
  navigation: {
    owner: [
      { to: '/portal/dashboard', icon: 'house', label: 'Inicio' },
      { to: '/portal/appointments', icon: 'calendar-days', label: 'Mis Citas' },
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
  },
  roleSwitcher: [
    { key: 'owner', label: 'Propietario', userId: 'o1' },
    { key: 'receptionist', label: 'Recepcionista', userId: '' },
    { key: 'vet', label: 'Veterinario', userId: 'v1' },
  ],
};
