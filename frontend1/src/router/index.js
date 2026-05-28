import { createRouter, createWebHistory } from 'vue-router';
import AppLayout from '@/components/layout/AppLayout.vue';
import Auth from '@/views/auth/Auth.vue';
import Login from '@/views/auth/Login.vue';
import Register from '@/views/auth/Register.vue';
import RecoverPassword from '@/views/auth/RecoverPassword.vue';
import OwnerDashboard from '@/views/owner/OwnerDashboard.vue';
import OwnerAppointments from '@/views/owner/OwnerAppointments.vue';
import OwnerHistory from '@/views/owner/OwnerHistory.vue';
import OwnerPets from '@/views/owner/OwnerPets.vue';
import OwnerPetForm from '@/views/owner/OwnerPetForm.vue';
import OwnerPetDetail from '@/views/owner/OwnerPetDetail.vue';
import OwnerProfile from '@/views/owner/OwnerProfile.vue';
import ReceptionDashboard from '@/views/receptionist/ReceptionDashboard.vue';
import AppointmentCalendar from '@/views/receptionist/AppointmentCalendar.vue';
import NewAppointment from '@/views/receptionist/NewAppointment.vue';
import CheckIn from '@/views/receptionist/CheckIn.vue';
import WaitList from '@/views/receptionist/WaitList.vue';
import OwnersSearch from '@/views/receptionist/OwnersSearch.vue';
import VetDashboard from '@/views/vet/VetDashboard.vue';
import VetPatients from '@/views/vet/VetPatients.vue';
import ClinicalRecords from '@/views/vet/ClinicalRecords.vue';
import RegisterConsultation from '@/views/vet/RegisterConsultation.vue';
import VaccineManager from '@/views/vet/VaccineManager.vue';
import DewormingManager from '@/views/vet/DewormingManager.vue';

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/login' },
    {
      path: '/auth',
      component: Auth,
      children: [
        {
          path: '/login',
          component: Login,
          meta: {
            title: 'Gestión Veterinaria de Excelencia',
            text: 'Cuidamos a los que más quieres con tecnología de punta y el mejor equipo de profesionales.',
            features: [
              { label: 'Atención personalizada', icon: '/src/assets/icon-personal.svg' },
              { label: 'Gestión de turnos ágil', icon: '/src/assets/icon-agile.svg' },
              { label: 'Historial clínico detallado', icon: '/src/assets/icon-history.svg' },
            ],
          },
        },
        {
          path: '/register',
          component: Register,
          meta: {
            title: 'Únete a nuestra comunidad',
            text: 'Comienza a gestionar la salud de tus mascotas de manera simple y rápida.',
            features: [
              { label: 'Perfiles de mascotas', icon: '/src/assets/icon-personal.svg' },
              { label: 'Recordatorios y alertas', icon: '/src/assets/icon-calendar.svg' },
              { label: 'Acceso 24/7 desde cualquier dispositivo', icon: '/src/assets/icon-agile.svg' },
            ],
          },
        },
        {
          path: '/recover-password',
          component: RecoverPassword,
          meta: {
            title: 'Recupera tu acceso',
            text: 'Sigue conectado con la mejor gestión para tu veterinaria o el cuidado de tu mascota.',
            features: [],
          },
        },
      ],
    },
    {
      path: '/portal',
      component: AppLayout,
      children: [
        { path: 'dashboard', component: OwnerDashboard },
        { path: 'appointments', component: OwnerAppointments },
        { path: 'pets', component: OwnerPets },
        { path: 'pets/add', component: OwnerPetForm },
        { path: 'pets/:id', component: OwnerPetDetail },
        { path: 'pets/:id/edit', component: OwnerPetForm },
        { path: 'history', component: OwnerHistory },
        { path: 'profile', component: OwnerProfile },
      ],
    },
    {
      path: '/reception',
      component: AppLayout,
      children: [
        { path: 'dashboard', component: ReceptionDashboard },
        { path: 'calendar', component: AppointmentCalendar },
        { path: 'new-appointment', component: NewAppointment },
        { path: 'checkin', component: CheckIn },
        { path: 'waitlist', component: WaitList },
        { path: 'owners', component: OwnersSearch },
      ],
    },
    {
      path: '/vet',
      component: AppLayout,
      children: [
        { path: 'dashboard', component: VetDashboard },
        { path: 'patients', component: VetPatients },
        { path: 'records', component: ClinicalRecords },
        { path: 'consultations', component: RegisterConsultation },
        { path: 'vaccines', component: VaccineManager },
        { path: 'dewormings', component: DewormingManager },
      ],
    },
    { path: '/:pathMatch(.*)*', redirect: '/portal/dashboard' },
  ],
});
