import { defineStore } from 'pinia';
import { appTemplate } from '@/config/appTemplate';
import http from '@/lib/http';
import { normalizeInventory, normalizeInventoryItem } from '@/lib/inventory';

export const useAppStore = defineStore('app', {
  state: () => ({
    role: localStorage.getItem('auth_role') || 'owner',
    currentUserId: localStorage.getItem('auth_user_id') || '',
    vets: [],
    owners: [],
    pets: [],
    appointments: [],
    consultations: [],
    vaccines: [],
    dewormings: [],
    waitingList: [],
    inventory: [],
    requisitions: [],
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
      
      // Auto-load related data when switching role
      if (role === 'technician' || role === 'manager') {
        this.fetchInventory().catch(err => console.error(err));
        this.fetchRequisitions().catch(err => console.error(err));
      }
    },

    // ==============================
    //  AUTH
    // ==============================
    async login(email, password) {
      const response = await http.post('/api/v1/auth/login/', { email, password });
      const { access, refresh, user } = response.data;
      
      localStorage.setItem('auth_token', access);
      localStorage.setItem('refresh_token', refresh);
      
      // Determine role from user groups
      let role = 'owner';
      const groups = user.groups || [];
      if (groups.includes('manager')) {
        role = 'manager';
      } else if (groups.includes('technician') || groups.includes('veterinary_technician')) {
        role = 'technician';
      } else if (groups.includes('receptionist')) {
        role = 'receptionist';
      } else if (groups.includes('veterinarian')) {
        role = 'vet';
      }
      
      this.role = role;
      localStorage.setItem('auth_role', role);
      
      if (role === 'owner') {
        await this.fetchProfile();
        await this.fetchPets();
      } else {
        this.currentUserId = user.id;
        localStorage.setItem('auth_user_id', user.id);
      }

      // Load role-specific data
      if (role === 'receptionist') {
        this.fetchAppointmentsToday().catch(e => console.error(e));
        this.fetchWaitingList().catch(e => console.error(e));
      } else if (role === 'vet') {
        this.fetchAppointmentsToday().catch(e => console.error(e));
        this.fetchAllPets().catch(e => console.error(e));
      } else if (role === 'technician' || role === 'manager') {
        this.fetchInventory().catch(e => console.error(e));
        this.fetchRequisitions().catch(e => console.error(e));
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
        dni: payload.dni || String(30000000 + Math.floor(Math.random() * 9999999)),
        location: 'Sede Palermo',
        emergency_contact: payload.phone || '+541155559999',
      };
      
      const res = await http.post('/api/v1/auth/register/', registerPayload);
      await this.login(payload.email, payload.password);
      return res.data;
    },

    logout() {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('auth_role');
      localStorage.removeItem('auth_user_id');
      this.role = 'owner';
      this.currentUserId = '';
      this.owners = [];
      this.pets = [];
      this.appointments = [];
      this.consultations = [];
      this.vaccines = [];
      this.dewormings = [];
      this.waitingList = [];
    },

    // ==============================
    //  OWNER PROFILE & PETS
    // ==============================
    async fetchProfile() {
      const res = await http.get('/api/v1/owners/me/');
      const data = res.data;
      const mappedOwner = {
        id: data.id,
        name: `${data.user.first_name} ${data.user.last_name}`.trim() || 'Propietario',
        email: data.user.email,
        phone: data.phone || '',
        address: data.address || '',
        dni: data.dni || '',
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
        dni: formData.dni,
      };
      
      const res = await http.patch('/api/v1/owners/me/', patchPayload);
      const data = res.data;
      const mappedOwner = {
        id: data.id,
        name: `${data.user.first_name} ${data.user.last_name}`.trim(),
        email: data.user.email,
        phone: data.phone || '',
        address: data.address || '',
        dni: data.dni || '',
        createdAt: data.created_at ? data.created_at.slice(0, 10) : '',
      };
      
      this.owners = this.owners.map(o => o.id === data.id ? mappedOwner : o);
      return mappedOwner;
    },

    async fetchOwners() {
      try {
        const res = await http.get('/api/v1/owners/');
        const data = res.data;
        const mappedOwners = data.map(owner => ({
          id: owner.id,
          name: `${owner.user.first_name} ${owner.user.last_name}`.trim() || owner.user.email,
          email: owner.user.email,
          phone: owner.phone || '',
          address: owner.address || '',
          dni: owner.dni || '',
          createdAt: owner.created_at ? owner.created_at.slice(0, 10) : '',
        }));
        this.owners = mappedOwners;
        return mappedOwners;
      } catch (e) {
        console.error('fetchOwners error:', e);
        return [];
      }
    },

    async fetchOwnerById(id) {
      const res = await http.get(`/api/v1/owners/${id}/`);
      const data = res.data;
      const mappedOwner = {
        id: data.id,
        name: `${data.user.first_name} ${data.user.last_name}`.trim() || data.user.email,
        email: data.user.email,
        phone: data.phone || '',
        address: data.address || '',
        dni: data.dni || '',
        createdAt: data.created_at ? data.created_at.slice(0, 10) : '',
      };
      const exists = this.owners.find(o => o.id === data.id);
      if (exists) {
        this.owners = this.owners.map(o => o.id === data.id ? mappedOwner : o);
      } else {
        this.owners.push(mappedOwner);
      }
      return mappedOwner;
    },

    async updateOwnerById(id, formData) {
      const nameParts = formData.name.trim().split(' ');
      const first_name = nameParts[0] || '';
      const last_name = nameParts.slice(1).join(' ') || '';
      
      const patchPayload = {
        first_name,
        last_name,
        phone: formData.phone,
        address: formData.address,
        dni: formData.dni,
      };
      
      const res = await http.patch(`/api/v1/owners/${id}/`, patchPayload);
      const data = res.data;
      const mappedOwner = {
        id: data.id,
        name: `${data.user.first_name} ${data.user.last_name}`.trim(),
        email: data.user.email,
        phone: data.phone || '',
        address: data.address || '',
        dni: data.dni || '',
        createdAt: data.created_at ? data.created_at.slice(0, 10) : '',
      };
      
      this.owners = this.owners.map(o => o.id === data.id ? mappedOwner : o);
      return mappedOwner;
    },

    async fetchPets() {
      const endpoint = this.role === 'owner' ? '/api/v1/owners/me/pets/' : '/api/v1/pets/';
      const res = await http.get(endpoint);
      const data = res.data;
      const mappedPets = data.map(pet => {
        const spec = (pet.species || '').toLowerCase();
        let species = 'other';
        if (spec.includes('canin') || spec.includes('perr') || spec.includes('dog')) species = 'dog';
        else if (spec.includes('felin') || spec.includes('gat') || spec.includes('cat')) species = 'cat';
        else if (spec.includes('ave') || spec.includes('bird')) species = 'bird';
        else if (spec.includes('conej') || spec.includes('rabbit')) species = 'rabbit';
        
        return {
          id: pet.id,
          ownerId: pet.owner?.id || pet.owner_id || this.currentUserId,
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
        color: petData.color || '',
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
        color: pet.color || petData.color || 'Marrón/Gris',
        microchip: pet.microchip_id || '',
      };
      
      this.pets.push(mappedPet);
      return mappedPet;
    },

    // ==============================
    //  APPOINTMENTS (Real API)
    // ==============================
    async fetchAppointments() {
      try {
        const res = await http.get('/api/v1/appointments/');
        this.appointments = res.data.map(this._mapAppointment);
      } catch (e) {
        console.error('fetchAppointments error:', e);
      }
    },

    async fetchAppointmentsToday() {
      try {
        const res = await http.get('/api/v1/appointments/today/');
        this.appointments = res.data.map(this._mapAppointment);
      } catch (e) {
        console.error('fetchAppointmentsToday error:', e);
      }
    },

    async createAppointment(payload) {
      // payload can be: { slot_id, patient_id, reason } OR { patient_id, reason, date, time }
      if (!payload.slot_id && payload.date && payload.time) {
        const vetId = 1; // Unico veterinario registrado en la DB de producción
        const slotsRes = await http.get(`/api/v1/vets/${vetId}/slots/`);
        const slots = slotsRes.data;
        
        const matchTime = payload.time.length === 5 ? `${payload.time}:00` : payload.time;
        let slot = slots.find(s => s.date === payload.date && s.start_time === matchTime && s.status === 'FREE');
        
        if (!slot) {
          throw new Error('El horario seleccionado ya no está disponible para esta fecha.');
        }
        
        payload.slot_id = slot.id;
      }

      const backendPayload = {
        slot_id: payload.slot_id,
        patient_id: payload.patient_id,
        reason: payload.reason || 'Consulta general',
      };

      const res = await http.post('/api/v1/appointments/', backendPayload);
      const appt = this._mapAppointment(res.data);
      this.appointments.push(appt);
      return appt;
    },


    async confirmAppointment(id) {
      await http.post(`/api/v1/appointments/${id}/confirm/`);
      await this.fetchAppointmentsToday();
    },

    async cancelAppointment(id) {
      await http.post(`/api/v1/appointments/${id}/cancel/`);
      await this.fetchAppointmentsToday();
    },

    async checkInAppointment(id, priority = 'MEDIUM') {
      await http.post(`/api/v1/appointments/${id}/check-in/`, { priority_level: priority });
      await this.fetchAppointmentsToday();
      await this.fetchWaitingList();
    },

    async saveConsultation(appointmentId, consultationData) {
      const res = await http.post(`/api/v1/appointments/${appointmentId}/consultations/`, consultationData);
      this.consultations.push(res.data);
      await this.fetchAppointmentsToday();
      return res.data;
    },

    // Map backend appointment to frontend shape
    _mapAppointment(appt) {
      return {
        id: appt.id,
        petId: appt.pet_id || appt.patient_id,
        petName: appt.patient_name || '',
        ownerId: appt.owner_id || '',
        ownerName: appt.owner_name || '',
        vetId: appt.vet_id || '',
        vetName: appt.vet_name || '',
        date: appt.date || '',
        time: appt.time || '',
        reason: appt.reason || appt.reason_for_visit || '',
        status: (appt.status || 'scheduled').toLowerCase(),
        notes: appt.notes || '',
      };
    },

    // ==============================
    //  WAITING LIST (Real API)
    // ==============================
    async fetchWaitingList() {
      try {
        const res = await http.get('/api/v1/waiting-list/');
        this.waitingList = res.data.map(entry => ({
          id: entry.id,
          patientName: entry.patient_name,
          ownerName: entry.owner_name,
          ownerId: entry.owner_id,
          appointmentId: entry.appointment_id,
          priority: entry.priority,
          status: entry.status,
          checkedInAt: entry.checked_in_at,
        }));
      } catch (e) {
        console.error('fetchWaitingList error:', e);
      }
    },

    async callNextPatient(waitingListId) {
      await http.post(`/api/v1/waiting-list/${waitingListId}/call-next/`);
      await this.fetchWaitingList();
      await this.fetchAppointmentsToday();
    },

    // ==============================
    //  VET SLOTS
    // ==============================
    async fetchVetSlots(vetId) {
      const res = await http.get(`/api/v1/vets/${vetId}/slots/`);
      return res.data;
    },

    // ==============================
    //  ALL PETS (for vet/receptionist)
    // ==============================
    async fetchAllPets() {
      try {
        // Use appointments data to populate pets list for vet views
        // The backend returns patient info with appointments
        // We keep what we have — pets are populated through appointment data
      } catch (e) {
        console.error('fetchAllPets error:', e);
      }
    },

    // ==============================
    //  MEDICAL RECORDS & VACCINES (Real API)
    // ==============================
    async fetchMedicalRecordSummary(petId) {
      const res = await http.get(`/api/v1/pets/${petId}/medical-record/summary/`);
      return res.data;
    },

    async fetchMedicalRecord(petId) {
      const res = await http.get(`/api/v1/pets/${petId}/medical-record/`);
      return res.data;
    },

    async fetchVaccinationSchedule(petId) {
      const res = await http.get(`/api/v1/pets/${petId}/vaccination-plan/schedule/`);
      return res.data;
    },

    async registerVaccinationEvent(petId, eventData) {
      const res = await http.post(`/api/v1/pets/${petId}/vaccination-events/`, eventData);
      return res.data;
    },

    // ==============================
    //  INVENTORY & REQUISITIONS (B2 - already working)
    // ==============================
    async fetchInventory() {
      const res = await http.get('/api/v1/inventory/supplies/');
      this.inventory = res.data.map(item => {
        const savedUmbral = localStorage.getItem(`inventory_umbral_${item.id}`);
        return {
          ...item,
          umbral: savedUmbral !== null ? parseInt(savedUmbral, 10) : item.umbral,
        };
      });
      normalizeInventory(this.inventory);
    },

    normalizeInventory() {
      normalizeInventory(this.inventory);
    },

    async addSupply(supplyData) {
      const payload = {
        name: supplyData.name,
        category: supplyData.category || 'CONSUMABLE',
        description: supplyData.description || '',
        min_stock: supplyData.min_stock || supplyData.umbral || 10,
      };
      const res = await http.post('/api/v1/inventory/supplies/', payload);
      const item = normalizeInventoryItem({
        ...res.data,
      });
      this.inventory.push(item);
      return item;
    },

    async addBatch(supplyId, { batch, expirationDate, quantity }) {
      const payload = {
        insumoId: supplyId,
        quantity: Number(quantity),
        batch: batch,
        expirationDate: expirationDate,
        acquisitionCost: "10.00"
      };
      
      await http.post('/api/v1/inventory/batches/', payload);
      await this.fetchInventory();
      return true;
    },

    async fetchRequisitions() {
      const res = await http.get('/api/v1/inventory/purchase-orders/');
      const data = res.data;
      this.requisitions = data.map(order => ({
        id: order.id,
        fecha: order.created_at ? order.created_at.slice(0, 10) : '',
        cantidadProductos: order.items.reduce((sum, item) => sum + item.quantity_requested, 0),
        total: parseFloat(order.total_cost),
        estado: order.status === 'REQUESTED' ? 'Pendiente' : 
                order.status === 'APPROVED' ? 'Aprobada' : 
                order.status === 'RECEIVED' ? 'Recibida' : 'Rechazada',
        items: order.items.map(item => ({
          insumoId: item.supply,
          quantity: item.quantity_requested
        }))
      }));
    },

    async addRequisition(requisitionData) {
      const items = requisitionData.items.map(item => {
        const supply = this.inventory.find(i => i.id === item.insumoId);
        return {
          insumoId: item.insumoId,
          nombre: supply?.name || 'Insumo Nuevo',
          cantidad: Number(item.quantity),
          costoUnitario: String(supply?.unitCost || 10.00)
        };
      });
      
      const payload = {
        proveedor: '554d23aa-4a60-4186-abfb-bdbc01312256',
        items: items
      };
      
      const res = await http.post('/api/v1/inventory/purchase-orders/', payload);
      await this.fetchRequisitions();
      return res.data;
    },

    async approveRequisition(orderId) {
      await http.post(`/api/v1/inventory/purchase-orders/${orderId}/approve/`);
      await this.fetchRequisitions();
      return true;
    },

    async cancelRequisition(orderId, reason = 'Cancelada por Gerencia') {
      await http.post(`/api/v1/inventory/purchase-orders/${orderId}/cancel/`, { reason });
      await this.fetchRequisitions();
      return true;
    },

    // ==============================
    //  LOCAL MUTATIONS (backwards compat)
    // ==============================
    addOwner(owner) {
      this.owners.push(owner);
    },
    updateOwner(owner) {
      this.owners = this.owners.map((item) => (item.id === owner.id ? owner : item));
    },
    updatePet(pet) {
      this.pets = this.pets.map((item) => (item.id === pet.id ? pet : item));
    },
    async addAppointment(appointmentData) {
      const vetId = 1; // Unico veterinario registrado en la DB de producción
      
      // Buscar slots disponibles del veterinario
      const slotsRes = await http.get(`/api/v1/vets/${vetId}/slots/`);
      const slots = slotsRes.data;
      
      const matchTime = appointmentData.time.length === 5 ? `${appointmentData.time}:00` : appointmentData.time;
      let slot = slots.find(s => s.date === appointmentData.date && s.start_time === matchTime && s.status === 'FREE');
      
      if (!slot) {
        throw new Error('El horario seleccionado ya no está disponible para esta fecha.');
      }
      
      const payload = {
        slot_id: slot.id,
        patient_id: appointmentData.petId,
        reason: appointmentData.reason || appointmentData.notes || 'Consulta general',
      };
      
      const res = await http.post('/api/v1/appointments/', payload);
      const appt = this._mapAppointment(res.data);
      this.appointments.push(appt);
      return appt;
    },
    updateAppointment(appointment) {
      this.appointments = this.appointments.map((item) =>
        item.id === appointment.id ? appointment : item
      );
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
  },
});
