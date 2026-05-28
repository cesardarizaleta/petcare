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
        // En el caso del Propietario, obtenemos su perfil completo, mascotas y turnos reales
        await this.fetchProfile();
        await this.fetchPets();
        await this.fetchAppointments();
      } else {
        this.currentUserId = user.id;
        localStorage.setItem('auth_user_id', user.id);
        await this.fetchAppointments();
        await this.fetchPets();
        if (role === 'receptionist') {
          await this.fetchOwners();
        }
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
    async fetchOwners() {
      const res = await http.get('/api/v1/owners/');
      const data = res.data;
      const mappedOwners = data.map(owner => ({
        id: owner.id,
        name: `${owner.user.first_name} ${owner.user.last_name}`.trim() || owner.user.email,
        email: owner.user.email,
        phone: owner.phone || '',
        address: owner.address || '',
        createdAt: owner.created_at ? owner.created_at.slice(0, 10) : '',
      }));
      this.owners = mappedOwners;
      return mappedOwners;
    },
    async fetchPets() {
      const endpoint = this.role === 'owner' ? '/api/v1/owners/me/pets/' : '/api/v1/pets/';
      const res = await http.get(endpoint);
      const data = res.data;
      const mappedPets = data.map(pet => {
        const spec = (pet.species || 'dog').toLowerCase();
        let species = 'other';
        if (spec.includes('canin') || spec.includes('perr') || spec.includes('dog')) species = 'dog';
        else if (spec.includes('felin') || spec.includes('gat') || spec.includes('cat')) species = 'cat';
        else if (spec.includes('ave') || spec.includes('bird')) species = 'bird';
        else if (spec.includes('conej') || spec.includes('rabbit')) species = 'rabbit';
        
        return {
          id: pet.id,
          ownerId: pet.owner_id || this.currentUserId,
          name: pet.name,
          species,
          breed: pet.breed || 'Mestizo',
          sex: pet.sex || 'M',
          birthDate: pet.date_of_birth || pet.birth_date,
          weight: pet.weight_kg || pet.weight || 0,
          color: pet.color || 'Marrón/Gris',
          microchip: pet.microchip_id || '',
        };
      });
      
      this.pets = mappedPets;
      
      // Cargar el historial clínico (consultas, vacunas, desparasitaciones) para todas las mascotas en segundo plano
      if (mappedPets.length > 0) {
        Promise.all(mappedPets.map(pet => this.fetchMedicalRecord(pet.id).catch(() => {})));
      }
      
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
        sex: petData.sex || 'M',
        birthDate: pet.date_of_birth || pet.birth_date,
        weight: pet.weight_kg || 0,
        color: petData.color || 'Dorado',
        microchip: pet.microchip_id || '',
      };
      
      this.pets.push(mappedPet);
      return mappedPet;
    },
    async updatePet(petData) {
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
      
      const res = await http.patch(`/api/v1/pets/${petData.id}/`, backendPayload);
      const pet = res.data;
      
      const mappedPet = {
        id: pet.id,
        ownerId: petData.ownerId || this.currentUserId,
        name: pet.name,
        species: petData.species || 'dog',
        breed: pet.breed || '',
        sex: petData.sex || 'M',
        birthDate: pet.date_of_birth || pet.birth_date,
        weight: pet.weight_kg || 0,
        color: petData.color || 'Dorado',
        microchip: pet.microchip_id || '',
      };
      
      this.pets = this.pets.map(p => p.id === pet.id ? mappedPet : p);
      return mappedPet;
    },
    async fetchMedicalRecord(petId) {
      const res = await http.get(`/api/v1/pets/${petId}/medical-record/`);
      const data = res.data;
      
      // Mapear consultas
      const mappedConsultations = (data.consultations || []).map((c, index) => ({
        id: c.id || `c-${petId}-${index}`,
        petId: petId,
        date: c.date,
        diagnosis: c.diagnosis,
        treatment: c.treatment,
        symptoms: c.symptoms,
        weight: c.weight,
        temperature: c.temperature,
        prescriptions: Array.isArray(c.prescriptions) ? c.prescriptions : (c.prescriptions ? c.prescriptions.split('\n') : []),
        notes: c.notes,
        followUpDate: c.follow_up_date,
      }));
      
      // Mapear vacunas y desparasitaciones
      const mappedVaccines = (data.vaccination_events || [])
        .filter(e => e.event_type === 'VACCINE')
        .map(e => ({
          id: e.id,
          petId: petId,
          name: e.dose,
          date: e.applied_date,
          nextDate: e.next_due_date,
          lot: e.lot,
        }));
        
      const mappedDewormings = (data.vaccination_events || [])
        .filter(e => e.event_type === 'DEWORMING')
        .map(e => ({
          id: e.id,
          petId: petId,
          product: e.dose,
          date: e.applied_date,
          nextDate: e.next_due_date,
          lot: e.lot,
        }));
        
      this.consultations = this.consultations.filter(c => c.petId !== petId).concat(mappedConsultations);
      this.vaccines = this.vaccines.filter(v => v.petId !== petId).concat(mappedVaccines);
      this.dewormings = this.dewormings.filter(d => d.petId !== petId).concat(mappedDewormings);
      
      return data;
    },
    async fetchAppointments() {
      const res = await http.get('/api/v1/appointments/');
      const data = res.data;
      
      this.appointments = data.map(appt => ({
        id: appt.id,
        petId: appt.pet_id,
        ownerId: appt.owner_id || this.currentUserId,
        vetId: appt.vet_id || 1,
        vetName: appt.vet_name || 'Veterinario',
        date: appt.date,
        time: appt.time ? appt.time.slice(0, 5) : '',
        reason: appt.reason,
        status: appt.status.toLowerCase(),
      }));
      return this.appointments;
    },
    async addAppointment(appointmentData) {
      const vetId = 1; // Unico veterinario registrado en la DB de producción
      
      // Buscar slots disponibles del veterinario
      const slotsRes = await http.get(`/api/v1/vets/${vetId}/slots/`);
      const slots = slotsRes.data;
      
      const matchTime = appointmentData.time.length === 5 ? `${appointmentData.time}:00` : appointmentData.time;
      let slot = slots.find(s => s.date === appointmentData.date && s.start_time === matchTime && s.status === 'FREE');
      
      if (!slot) {
        slot = slots.find(s => s.date === appointmentData.date && s.status === 'FREE');
      }
      if (!slot) {
        slot = slots.find(s => s.status === 'FREE');
      }
      if (!slot) {
        throw new Error('No hay turnos disponibles para este veterinario.');
      }
      
      const payload = {
        slot_id: slot.id,
        patient_id: appointmentData.petId,
        reason: appointmentData.reason || appointmentData.notes || 'Consulta general',
      };
      
      const res = await http.post('/api/v1/appointments/', payload);
      const appt = res.data;
      
      const mappedAppt = {
        id: appt.id,
        petId: appt.pet_id,
        ownerId: appointmentData.ownerId || appt.owner_id || this.currentUserId,
        vetId: appt.vet_id || 1,
        vetName: appt.vet_name || 'Veterinario',
        date: appt.date,
        time: appt.time ? appt.time.slice(0, 5) : '',
        reason: appt.reason,
        status: appt.status.toLowerCase(),
      };
      
      this.appointments.push(mappedAppt);
      return mappedAppt;
    },
    async updateAppointment(appointment) {
      const id = appointment.id;
      
      try {
        if (appointment.status === 'cancelled') {
          await http.post(`/api/v1/appointments/${id}/cancel/`);
        } else if (appointment.status === 'confirmed') {
          await http.post(`/api/v1/appointments/${id}/confirm/`);
        } else if (appointment.status === 'waiting') {
          await http.post(`/api/v1/appointments/${id}/check-in/`, { priority_level: 'MEDIUM' });
        }
      } catch (error) {
        console.error('Error updating appointment status in backend:', error);
      }
      
      this.appointments = this.appointments.map((item) =>
        item.id === appointment.id ? { ...appointment, status: appointment.status.toLowerCase() } : item
      );
    },
    async cancelAppointment(id, cancelReason = '') {
      await http.post(`/api/v1/appointments/${id}/cancel/`);
      
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
    async addConsultation(consultationData) {
      const payload = {
        diagnosis: consultationData.diagnosis,
        treatment: consultationData.treatment,
        symptoms: consultationData.symptoms,
        weight: String(consultationData.weight),
        temperature: String(consultationData.temperature),
        prescriptions: Array.isArray(consultationData.prescriptions) 
          ? consultationData.prescriptions.join('\n') 
          : consultationData.prescriptions,
        notes: consultationData.notes,
        follow_up_date: consultationData.followUpDate || '',
      };
      
      const res = await http.post(`/api/v1/appointments/${consultationData.appointmentId}/consultations/`, payload);
      const data = res.data;
      
      const mapped = {
        id: `c${Date.now()}`,
        appointmentId: consultationData.appointmentId,
        petId: consultationData.petId,
        vetId: consultationData.vetId,
        date: data.date,
        weight: Number(data.weight) || 0,
        temperature: Number(data.temperature) || 0,
        symptoms: data.symptoms,
        diagnosis: data.diagnosis,
        treatment: data.treatment,
        prescriptions: data.prescriptions ? data.prescriptions.split('\n') : [],
        followUpDate: data.follow_up_date || undefined,
        notes: data.notes,
      };
      
      this.consultations.push(mapped);
      
      // Cambiar estado local del turno a completado
      this.appointments = this.appointments.map(appt => 
        appt.id === consultationData.appointmentId ? { ...appt, status: 'completed' } : appt
      );
      
      return mapped;
    },
    async addVaccine(vaccineData) {
      const payload = {
        event_type: 'VACCINE',
        dose: vaccineData.name,
        applied_date: vaccineData.date,
        sanitary_batch: vaccineData.lot || '',
        next_due_date: vaccineData.nextDate,
      };
      
      const res = await http.post(`/api/v1/pets/${vaccineData.petId}/vaccination-events/`, payload);
      const event = res.data;
      
      const mapped = {
        id: event.id,
        petId: vaccineData.petId,
        name: event.dose,
        date: event.applied_date,
        nextDate: event.next_due_date,
        lot: event.lot,
      };
      
      this.vaccines.push(mapped);
      return mapped;
    },
    async addDeworming(dewormingData) {
      const payload = {
        event_type: 'DEWORMING',
        dose: dewormingData.product,
        applied_date: dewormingData.date,
        sanitary_batch: dewormingData.notes || '',
        next_due_date: dewormingData.nextDate,
      };
      
      const res = await http.post(`/api/v1/pets/${dewormingData.petId}/vaccination-events/`, payload);
      const event = res.data;
      
      const mapped = {
        id: event.id,
        petId: dewormingData.petId,
        product: event.dose,
        date: event.applied_date,
        nextDate: event.next_due_date,
        lot: event.lot,
      };
      
      this.dewormings.push(mapped);
      return mapped;
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
