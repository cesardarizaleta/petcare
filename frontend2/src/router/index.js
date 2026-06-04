import { createRouter, createWebHistory } from 'vue-router';
import AppLayout from '@/components/layout/AppLayout.vue';
import Login from '@/views/auth/Login.vue';
import Register from '@/views/auth/Register.vue';
import OwnerDashboard from '@/views/owner/OwnerDashboard.vue';
import OwnerAppointments from '@/views/owner/OwnerAppointments.vue';
import OwnerHistory from '@/views/owner/OwnerHistory.vue';
import OwnerPets from '@/views/owner/OwnerPets.vue';
import OwnerProfile from '@/views/owner/OwnerProfile.vue';
import ScheduleAppointment from '@/views/owner/ScheduleAppointment.vue';
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
import RegisterSupply from '@/views/technician/RegisterSupply.vue';
import InventoryCatalog from '@/views/technician/InventoryCatalog.vue';
import RepositionStock from '@/views/technician/RepositionStock.vue';
import SupplyRequisition from '@/views/technician/SupplyRequisition.vue';
import RequestDashboard from '@/views/technician/RequestDashboard.vue';
import RequestPanel from '@/views/manager/RequestPanel.vue';
import DashboardView from '@/views/manager/DashboardView.vue';

// Map of route prefixes to allowed roles
const routeRoleMap = {
  '/portal': ['owner'],
  '/reception': ['receptionist'],
  '/vet': ['vet', 'veterinarian'],
  '/technician': ['technician'],
  '/manager': ['manager'],
  '/superadmin': ['superadmin'],
};

// Role-based default dashboards
const roleDashboardMap = {
  owner: '/portal/dashboard',
  receptionist: '/reception/dashboard',
  vet: '/vet/dashboard',
  veterinarian: '/vet/dashboard',
  technician: '/technician/inventory',
  manager: '/manager/dashboard',
  superadmin: '/superadmin/dashboard',
};

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/login' },
    { path: '/login', component: Login, meta: { public: true } },
    { path: '/register', component: Register, meta: { public: true } },
    {
      path: '/portal',
      component: AppLayout,
      meta: { requiredRole: 'owner' },
      children: [
        { path: 'dashboard', component: OwnerDashboard },
        { path: 'appointments', component: OwnerAppointments },
        { path: 'schedule', component: ScheduleAppointment },
        { path: 'pets', component: OwnerPets },
        { path: 'history', component: OwnerHistory },
        { path: 'profile', component: OwnerProfile },
      ],
    },
    {
      path: '/reception',
      component: AppLayout,
      meta: { requiredRole: 'receptionist' },
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
      meta: { requiredRole: 'vet' },
      children: [
        { path: 'dashboard', component: VetDashboard },
        { path: 'patients', component: VetPatients },
        { path: 'records', component: ClinicalRecords },
        { path: 'consultations', component: RegisterConsultation },
        { path: 'vaccines', component: VaccineManager },
        { path: 'dewormings', component: DewormingManager },
      ],
    },
    {
      path: '/technician',
      component: AppLayout,
      meta: { requiredRole: 'technician' },
      children: [
        { path: 'inventory', component: InventoryCatalog },
        { path: 'register-supply', component: RegisterSupply },
        { path: 'form', redirect: '/technician/register-supply' },
        { path: 'reposition', component: RepositionStock },
        { path: 'supply-requisition', component: SupplyRequisition },
        { path: 'interface', redirect: '/technician/supply-requisition' },
        { path: 'tracking', component: RequestDashboard },
      ],
    },
    {
      path: '/manager',
      component: AppLayout,
      meta: { requiredRole: 'manager' },
      children: [
        { path: 'dashboard', name: 'ManagerDashboard', component: DashboardView },
        { path: 'requests', component: RequestPanel },
      ],
    },
    {
      path: '/superadmin',
      component: AppLayout,
      meta: { requiredRole: 'superadmin' },
      children: [
        { path: 'dashboard', component: () => import('@/views/superadmin/SuperAdminDashboard.vue') },
      ],
    },
    { path: '/:pathMatch(.*)*', redirect: '/login' },
  ],
});

// --- Navigation Guards ---
router.beforeEach((to, from, next) => {
  const isPublic = to.meta.public === true || to.matched.some(r => r.meta.public);
  const token = localStorage.getItem('auth_token');
  const role = localStorage.getItem('auth_role') || 'owner';

  // 1. If not logged in and route is protected, redirect to login
  if (!isPublic && !token) {
    return next('/login');
  }

  // 2. If logged in and going to login/register, redirect to dashboard
  if (isPublic && token && (to.path === '/login' || to.path === '/register')) {
    return next(roleDashboardMap[role] || '/portal/dashboard');
  }

  // 3. Check role-based access
  const matchedRoute = to.matched.find(r => r.meta.requiredRole);
  if (matchedRoute) {
    const requiredRole = matchedRoute.meta.requiredRole;
    // Allow access if the user's role matches the required role
    const isAllowed = role === requiredRole || 
      (requiredRole === 'vet' && role === 'veterinarian') ||
      (requiredRole === 'veterinarian' && role === 'vet');
    
    if (!isAllowed) {
      return next(roleDashboardMap[role] || '/login');
    }
  }

  next();
});
