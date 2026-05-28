import { defineStore } from 'pinia';
import { appTemplate } from '@/config/appTemplate';
import http from '@/lib/http';
import {
  vets as seedVets,
  owners as seedOwners,
  pets as seedPets,
  appointments as seedAppointments,
  consultations as seedConsultations,
  vaccines as seedVaccines,
  dewormings as seedDewormings,
} from '@/data/mockData';

const shiftDate = (dateStr) => {
  if (!dateStr) return dateStr;
  const base = new Date('2026-05-08T12:00:00').getTime();
  const today = new Date();
  today.setHours(12, 0, 0, 0);
  const diff = today.getTime() - base;
  const d = new Date(dateStr + 'T12:00:00');
  d.setTime(d.getTime() + diff);
  return d.toISOString().slice(0, 10);
};

const mapDates = (item) => {
  const newItem = { ...item };
  if (newItem.date) newItem.date = shiftDate(newItem.date);
  if (newItem.nextDate) newItem.nextDate = shiftDate(newItem.nextDate);
  if (newItem.birthDate) newItem.birthDate = shiftDate(newItem.birthDate);
  if (newItem.createdAt) newItem.createdAt = shiftDate(newItem.createdAt);
  if (newItem.followUpDate) newItem.followUpDate = shiftDate(newItem.followUpDate);
  return newItem;
};

const clone = (value) => value.map((item) => mapDates({ ...item }));

export const useAppStore = defineStore('app', {
  state: () => ({
    role: localStorage.getItem('auth_role') || 'owner',
    currentUserId: localStorage.getItem('auth_user_id') || 'o1',
    vets: clone(seedVets),
    owners: clone(seedOwners),
    pets: clone(seedPets),
    appointments: clone(seedAppointments),
    consultations: clone(seedConsultations),
    vaccines: clone(seedVaccines),
    dewormings: clone(seedDewormings),
    notifications: [],
  }),
  getters: {
    currentOwner(state) {
      return state.owners.find((owner) => owner.id === state.currentUserId) || null;
    },
    roleInfo(state) {
      return appTemplate.roles[state.role];
    },
    roleNavigation(state) {
      return appTemplate.navigation[state.role];
    },
  },
  actions: {
    setRole(role, userId = undefined) {
      this.role = role;
      localStorage.setItem('auth_role', role);
      if (userId !== undefined) {
        this.currentUserId = userId;
        localStorage.setItem('auth_user_id', userId);
      }
    },
    async login(email, password) {
      const response = await http.post('/api/v1/auth/login/', { email, password });
      const { access, refresh, user } = response.data;
      
      localStorage.setItem('auth_token', access);
      localStorage.setItem('refresh_token', refresh);
      
      // Determinar el rol del usuario basado en sus grupos de seguridad
      let role = 'owner';
      if (user.groups.includes('receptionist')) {
        role = 'receptionist';
      } else if (user.groups.includes('veterinarian')) {
        role = 'vet';
      }
      
      this.role = role;
      localStorage.setItem('auth_role', role);
      
      if (role === 'owner') {
        // En el caso del Propietario, obtenemos su perfil completo y su lista de mascotas reales
        const ownerProfile = await this.fetchProfile();
        await this.fetchPets();
      } else {
        this.currentUserId = user.id;
        localStorage.setItem('auth_user_id', user.id);
      }
      
      return user;
    },
    async register(payload) {
      const nameParts = payload.name.trim().split(' ');
      const first_name = nameParts[0] || 'Nuevo';
      const last_name = nameParts.slice(1).join(' ') || 'Propietario';
      
      const registerPayload = {
        email: payload.email,
        password: payload.password,
        first_name,
        last_name,
        phone: payload.phone || '+541155554444',
        address: payload.address || 'Av. Libertador 1420, CABA',
        dni: String(30000000 + Math.floor(Math.random() * 9999999)),
        location: 'Sede Palermo',
        emergency_contact: payload.phone || '+541155559999',
      };
      
      const res = await http.post('/api/v1/auth/register/', registerPayload);
      // Tras registrar con éxito, iniciamos sesión automáticamente para obtener tokens
      await this.login(payload.email, payload.password);
      return res.data;
    },
    async fetchProfile() {
      const res = await http.get('/api/v1/owners/me/');
      const data = res.data;
      const mappedOwner = {
        id: data.id,
        name: `${data.user.first_name} ${data.user.last_name}`.trim() || 'Propietario',
        email: data.user.email,
        phone: data.phone || '',
        address: data.address || '',
        createdAt: data.created_at ? data.created_at.slice(0, 10) : '',
      };
      
      this.currentUserId = data.id;
      localStorage.setItem('auth_user_id', data.id);
      
      const exists = this.owners.find(o => o.id === data.id);
      if (exists) {
        this.owners = this.owners.map(o => o.id === data.id ? mappedOwner : o);
      } else {
        this.owners.push(mappedOwner);
      }
      return mappedOwner;
    },
    async updateProfile(formData) {
      const nameParts = formData.name.trim().split(' ');
      const first_name = nameParts[0] || '';
      const last_name = nameParts.slice(1).join(' ') || '';
      
      const patchPayload = {
        first_name,
        last_name,
        phone: formData.phone,
        address: formData.address,
      };
      
      const res = await http.patch('/api/v1/owners/me/', patchPayload);
      const data = res.data;
      const mappedOwner = {
        id: data.id,
        name: `${data.user.first_name} ${data.user.last_name}`.trim(),
        email: data.user.email,
        phone: data.phone || '',
        address: data.address || '',
        createdAt: data.created_at ? data.created_at.slice(0, 10) : '',
      };
      
      this.owners = this.owners.map(o => o.id === data.id ? mappedOwner : o);
      return mappedOwner;
    },
    async fetchPets() {
      const res = await http.get('/api/v1/owners/me/pets/');
      const data = res.data;
      const mappedPets = data.map(pet => {
        const spec = pet.species.toLowerCase();
        let species = 'other';
        if (spec.includes('canin') || spec.includes('perr')) species = 'dog';
        else if (spec.includes('felin') || spec.includes('gat')) species = 'cat';
        else if (spec.includes('ave')) species = 'bird';
        else if (spec.includes('conej')) species = 'rabbit';
        
        return {
          id: pet.id,
          ownerId: this.currentUserId,
          name: pet.name,
          species,
          breed: pet.breed || 'Mestizo',
          birthDate: pet.date_of_birth || pet.birth_date,
          weight: pet.weight_kg || 0,
          color: pet.color || 'Marrón/Gris',
          microchip: pet.microchip_id || '',
        };
      });
      
      this.pets = mappedPets;
      return mappedPets;
    },
    async addPet(petData) {
      const speciesMap = {
        dog: 'Canino',
        cat: 'Felino',
        bird: 'Ave',
        rabbit: 'Conejo',
        other: 'Otro'
      };
      const backendPayload = {
        name: petData.name,
        species: speciesMap[petData.species] || petData.species || 'Otro',
        breed: petData.breed || '',
        date_of_birth: petData.birthDate || petData.date_of_birth,
        sex: petData.sex || 'M',
        weight_kg: parseFloat(petData.weight) || 0,
      };
      
      const res = await http.post('/api/v1/owners/me/pets/', backendPayload);
      const pet = res.data;
      
      const mappedPet = {
        id: pet.id,
        ownerId: this.currentUserId,
        name: pet.name,
        species: petData.species || 'dog',
        breed: pet.breed || '',
        birthDate: pet.date_of_birth || pet.birth_date,
        weight: pet.weight_kg || 0,
        color: petData.color || 'Dorado',
        microchip: pet.microchip_id || '',
      };
      
      this.pets.push(mappedPet);
      return mappedPet;
    },
    logout() {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('auth_role');
      localStorage.removeItem('auth_user_id');
      this.role = 'owner';
      this.currentUserId = '';
    },
    addOwner(owner) {
      this.owners.push(owner);
    },
    updateOwner(owner) {
      this.owners = this.owners.map((item) => (item.id === owner.id ? owner : item));
    },
    updatePet(pet) {
      this.pets = this.pets.map((item) => (item.id === pet.id ? pet : item));
    },
    addAppointment(appointment) {
      this.appointments.push(appointment);
    },
    updateAppointment(appointment) {
      this.appointments = this.appointments.map((item) =>
        item.id === appointment.id ? appointment : item
      );
    },
    cancelAppointment(id, cancelReason = '') {
      this.appointments = this.appointments.map((item) =>
        item.id === id ? { ...item, status: 'cancelled', cancelReason } : item
      );
      this.addNotification({
        title: 'Cita cancelada',
        description: `La cita ha sido cancelada${cancelReason ? ' (' + cancelReason + ')' : ''}.`,
        type: 'info',
        date: new Date().toISOString()
      });
    },
    addConsultation(consultation) {
      this.consultations.push(consultation);
    },
    addVaccine(vaccine) {
      this.vaccines.push(vaccine);
    },
    addDeworming(deworming) {
      this.dewormings.push(deworming);
    },
    addNotification(notification) {
      this.notifications.unshift({
        id: `n${Date.now()}`,
        read: false,
        ...notification
      });
    },
    markNotificationAsRead(id) {
      const notif = this.notifications.find(n => n.id === id);
      if (notif) notif.read = true;
    },
  },
});

