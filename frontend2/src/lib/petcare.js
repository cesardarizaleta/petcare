export const statusMeta = {
  scheduled: { label: 'Programada', className: 'chip--brand' },
  confirmed: { label: 'Confirmada', className: 'chip--success' },
  in_progress: { label: 'En Consulta', className: 'chip--warning' },
  completed: { label: 'Completada', className: 'chip--sage' },
  cancelled: { label: 'Cancelada', className: 'chip--danger' },
  waiting: { label: 'En Espera', className: 'chip--cream' },
  checked_in: { label: 'Chequeada', className: 'chip--cream' },
};

export const speciesMeta = {
  dog: { label: 'Perro', icon: 'dog', className: 'chip--brand' },
  cat: { label: 'Gato', icon: 'cat', className: 'chip--sage' },
  bird: { label: 'Ave', icon: 'bird', className: 'chip--cream' },
  rabbit: { label: 'Conejo', icon: 'rabbit', className: 'chip--warning' },
  other: { label: 'Otro', icon: 'paw-print', className: 'chip--brand' },
};

export function formatDate(value, locale = 'es-AR') {
  if (!value) return '—';
  return new Intl.DateTimeFormat(locale, {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  }).format(new Date(`${value}T12:00:00`));
}

export function formatDateLong(value, locale = 'es-AR') {
  if (!value) return '—';
  return new Intl.DateTimeFormat(locale, { weekday: 'long', day: 'numeric', month: 'long' }).format(
    new Date(`${value}T12:00:00`)
  );
}

export function formatMoney(
  value,
  { locale = 'es-AR', currency = 'ARS', maximumFractionDigits = 0 } = {}
) {
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency,
    maximumFractionDigits,
  }).format(value);
}

export function todayISO() {
  return new Date().toISOString().slice(0, 10);
}

export function getOwner(owners, ownerId) {
  return owners.find((owner) => owner.id === ownerId);
}

export function getPet(pets, petId) {
  return pets.find((pet) => pet.id === petId);
}

export function getVet(vets, vetId) {
  return vets.find((vet) => vet.id === vetId);
}

export function getOwnerPets(pets, ownerId) {
  return pets.filter((pet) => pet.ownerId === ownerId);
}

export function getOwnerAppointments(appointments, ownerId) {
  return appointments
    .filter((appointment) => appointment.ownerId === ownerId)
    .slice()
    .sort(sortAppointments);
}

export function getPetAppointments(appointments, petId) {
  return appointments
    .filter((appointment) => appointment.petId === petId)
    .slice()
    .sort(sortAppointments);
}

export function getPetConsultations(consultations, petId) {
  return consultations
    .filter((consultation) => consultation.petId === petId)
    .slice()
    .sort(sortByDateDesc);
}

export function getPetVaccines(vaccines, petId) {
  return vaccines
    .filter((item) => item.petId === petId)
    .slice()
    .sort(sortByDateDesc);
}

export function getPetDewormings(dewormings, petId) {
  return dewormings
    .filter((item) => item.petId === petId)
    .slice()
    .sort(sortByDateDesc);
}

export function getAppointmentsByDate(appointments, date) {
  return appointments
    .filter((appointment) => appointment.date === date)
    .slice()
    .sort(sortAppointments);
}

export function getTodayAppointments(appointments) {
  // No more hardcoded date — appointments come from the backend's /today/ endpoint
  // Just return all appointments (they're already filtered to today by the API)
  return appointments.slice().sort(sortAppointments);
}

export function sortAppointments(left, right) {
  return `${left.date} ${left.time}`.localeCompare(`${right.date} ${right.time}`);
}

function sortByDateDesc(left, right) {
  return `${right.date}`.localeCompare(`${left.date}`);
}

export function countByStatus(appointments, status) {
  return appointments.filter((appointment) => appointment.status === status).length;
}

export function countUpcoming(appointments) {
  const today = todayISO();
  return appointments.filter(
    (appointment) => appointment.date >= today && appointment.status !== 'cancelled'
  ).length;
}

export function countCompleted(appointments) {
  return appointments.filter((appointment) => appointment.status === 'completed').length;
}

export function countWaiting(appointments) {
  return appointments.filter(
    (appointment) => appointment.status === 'waiting' || appointment.status === 'checked_in'
  ).length;
}

export function getAppointmentStats(appointments) {
  return {
    scheduled: countByStatus(appointments, 'scheduled'),
    confirmed: countByStatus(appointments, 'confirmed'),
    in_progress: countByStatus(appointments, 'in_progress'),
    completed: countCompleted(appointments),
    waiting: countWaiting(appointments),
  };
}

export function getAppointmentsByVet(appointments, vetId) {
  return appointments
    .filter((appointment) => appointment.vetId === vetId)
    .slice()
    .sort(sortAppointments);
}

export function getLatestConsultation(consultations, petId) {
  return getPetConsultations(consultations, petId)[0] || null;
}

export function getLatestVaccine(vaccines, petId) {
  return getPetVaccines(vaccines, petId)[0] || null;
}

export function getLatestDeworming(dewormings, petId) {
  return getPetDewormings(dewormings, petId)[0] || null;
}

export function daysFromNow(days) {
  const date = new Date();
  date.setDate(date.getDate() + days);
  return date.toISOString().slice(0, 10);
}

export const timeSlots = [
  '09:00', '09:30', '10:00', '10:30', '11:00', '11:30',
  '14:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00',
];

/**
 * Extrae un mensaje legible de un error Axios del backend.
 * Soporta: { error: "..." }, { detail: "..." }, { message: "..." },
 * errores de validación DRF { field: ["msg"] }, y fallback genérico.
 */
export function extractApiError(err, fallback = 'Ocurrió un error inesperado.') {
  const data = err?.response?.data;
  if (!data) return err?.message || fallback;

  // Respuesta directa con campo error, detail o message
  if (typeof data === 'string') return data;
  if (data.error) return data.error;
  if (data.detail) return data.detail;
  if (data.message) return data.message;

  // Errores de validación DRF: { field: ["msg1", "msg2"] }
  const fieldErrors = Object.entries(data)
    .filter(([, v]) => Array.isArray(v))
    .map(([key, msgs]) => `${key}: ${msgs.join(', ')}`)
    .join(' | ');
  if (fieldErrors) return fieldErrors;

  // Non-field errors
  if (data.non_field_errors) return data.non_field_errors.join(', ');

  return fallback;
}
