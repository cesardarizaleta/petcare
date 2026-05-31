# Plan de Pruebas y Checklist de Actividades por Módulo

Este documento compila de forma estructurada los requisitos del sistema **PetCare**, divididos por módulos, definiendo las **actividades de desarrollo/configuración** y las **pruebas detalladas a realizar** para garantizar el cumplimiento y la calidad en cada escenario.

---

## 🔐 Módulo Transversal: Seguridad y Base de Datos

Garantiza el control de acceso basado en roles, cifrado, persistencia, atomicidad de transacciones y consistencia de las sesiones.

### 📋 Checklist de Actividades
- [x] Configurar el modelo de usuario personalizado (`User` hereda de `AbstractUser` usando `email` como identificador único).
- [x] Diseñar e implementar los grupos de seguridad del sistema (`owner`, `receptionist`, `veterinarian`, `manager`, `technician`, `veterinary_technician`).
- [x] Desarrollar la autenticación de usuarios basada en tokens JWT (SimpleJWT).
- [x] Configurar clases de permisos en el backend (`IsOwner`, `IsReceptionist`, `IsVeterinaryTechnician`, `IsManager`, `DjangoModelPermissions`).
- [x] Crear el middleware de auditoría o tabla `AuditLog` para el registro de operaciones sensibles.
- [ ] Configurar políticas de expiración de sesión por inactividad.
- [ ] Configurar el sistema de copias de seguridad automáticas (backups) para la base de datos sqlite/postgresql.

### 🧪 Pruebas a Realizar (QA & Verificación)
- [x] **Prueba de Autenticación de Usuarios:**
  - *Procedimiento:* Consumir `POST /api/v1/auth/login/` con credenciales válidas e inválidas.
  - *Resultado esperado:* Con credenciales válidas retorna token de `access`, `refresh` y datos del usuario. Con credenciales inválidas retorna `401 Unauthorized`.
- [x] **Prueba de Autorización y Restricción por Roles:**
  - *Procedimiento:* Intentar ingresar al panel del Gerente `/api/v1/users/manager/` utilizando un token de usuario con rol `receptionist` o `owner`.
  - *Resultado esperado:* El backend debe retornar `403 Forbidden`, bloqueando el acceso al no contar con el grupo de seguridad apropiado.
- [x] **Prueba de Auditoría (Audit Logs):**
  - *Procedimiento:* Realizar un consumo de insumos o actualización sensible e inspeccionar la tabla `AuditLog`.
  - *Resultado esperado:* El sistema registra de forma automática la fecha, el usuario, la acción y la ruta de la operación realizada.
- [ ] **Prueba de Transaccionalidad y Consistencia:**
  - *Procedimiento:* Simular una falla en la mitad de la creación de una orden de compra (por ejemplo, enviando un insumo inexistente).
  - *Resultado esperado:* Django revierte la transacción (`@transaction.atomic`), evitando que queden registros huérfanos de la orden de compra en la base de datos.
- [ ] **Prueba de Expiración de Sesión:**
  - *Procedimiento:* Configurar un tiempo de inactividad corto y verificar que el token de acceso requiera renovación o redireccione al Login.
  - *Resultado esperado:* Cierre de sesión automático tras el período establecido de inactividad.

---

## 🐕 Módulo 1: Gestión de Clientes, Mascotas, Citas y Atención Clínica

Contempla los flujos de interacción de los **Propietarios**, **Recepcionistas** y **Veterinarios** en relación con las agendas, historial médico y estado de pacientes.

### 📋 Checklist de Actividades

#### 👤 Submódulo Propietario (Portal Web del Cliente)
- [x] Desarrollar formulario de registro en frontend (`Register.vue`) conectado a `POST /api/v1/auth/register/`.
- [x] Diseñar vistas de gestión de perfil e información básica de contacto.
- [x] Desarrollar vista de gestión de mascotas (crear, editar atributos básicos de la mascota).
- [x] Implementar funcionalidad para que el propietario pueda agendar y cancelar citas en línea.
- [x] Implementar consulta del historial de citas completadas y pendientes.

#### 📞 Submódulo Recepcionista (Atención y Agenda)
- [x] Diseñar el dashboard de citas del día en formato de tablero visual.
- [x] Implementar calendario interactivo para consultar la disponibilidad de atención de los veterinarios.
- [x] Desarrollar formulario para registrar citas manualmente (para llamadas o presencial).
- [x] Implementar registro de asistencia de los pacientes (Check-in).
- [x] Crear y gestionar la lista de espera dinámica en tiempo real de los pacientes que asisten.
- [x] Proveer buscadores rápidos de propietarios y su relación con las mascotas correspondientes.

#### 🩺 Submódulo Veterinario (Atención Médica)
- [x] Desarrollar vista de pacientes asignados del día.
- [x] Diseñar visualizador del expediente e historial clínico completo de un paciente (mascota).
- [x] Diseñar formulario de consulta médica que permita registrar: síntomas, diagnóstico y observaciones.
- [x] Conectar el registro de consultas médicas con el consumo automático de insumos en inventario (relación Módulos 1 y 2).
- [x] Desarrollar gestor de planes de vacunación y desparasitación (cronograma, dosis aplicadas y eventos).

### 🧪 Pruebas a Realizar (QA & Verificación)
- [x] **Prueba de Auto-Registro de Propietario:**
  - *Procedimiento:* Registrar un usuario en `/register` llenando Nombre, Email, Password, Teléfono y Dirección.
  - *Resultado esperado:* Crea el `User` base, le asigna el rol `owner`, crea su `NaturalPerson` y su perfil de `Owner`. Inicia sesión automáticamente redirigiendo al portal.
- [x] **Prueba de Agendamiento Online vs Calendario del Veterinario:**
  - *Procedimiento:* Un propietario agenda una cita para una fecha y hora específica con un veterinario.
  - *Resultado esperado:* La cita aparece en la agenda del propietario, se bloquea la disponibilidad en el calendario de la recepcionista y se visualiza en el día del veterinario asignado.
- [x] **Prueba de Flujo de Citas (Check-in -> Lista de Espera -> Consulta):**
  - *Procedimiento:* 
    1. Recepcionista marca Check-in a un paciente que asiste físicamente a su cita.
    2. El paciente ingresa automáticamente a la Lista de Espera del día.
    3. El veterinario atiende al paciente desde su lista de pacientes, iniciando la Consulta.
  - *Resultado esperado:* El estado de la cita transiciona de `Programada` -> `Presente` -> `En Curso` -> `Completada`, actualizándose los tableros de recepcionista y veterinario.
- [x] **Prueba de Registro de Consulta e Historial Clínico:**
  - *Procedimiento:* El veterinario registra un diagnóstico y prescribe un tratamiento de desparasitación.
  - *Resultado esperado:* Los datos de la consulta se guardan y se añaden cronológicamente al expediente del paciente, permitiendo su consulta posterior.
- [ ] **Prueba de Notificaciones y Recordatorios:**
  - *Procedimiento:* Simular el envío automático de un recordatorio de cita al propietario (vía correo o mock de notificación).
  - *Resultado esperado:* El propietario recibe la notificación de confirmación del evento con los datos de fecha, hora y sede.

---

## 📦 Módulo 2: Inventario, Reabastecimiento y Tablero Gerencial

Contempla los flujos de control de inventario de medicamentos e insumos por parte del **Técnico Veterinario**, y la supervisión financiera e indicadores clave por parte del **Gerente**.

### 📋 Checklist de Actividades

#### 🧪 Submódulo Técnico Veterinario (Inventario y Reposición)
- [x] Implementar el catálogo digital de medicamentos e insumos especificando costos unitarios.
- [x] Desarrollar el sistema de consulta de existencias agrupado por lotes/lotes físicos de stock (`SupplyBatch`).
- [x] Desarrollar lógica de consumo de insumos automatizado en base a reglas (FIFO - Primero en Entrar, Primero en Salir) al realizar consultas médicas.
- [x] Implementar alertas visuales y de sistema cuando el stock actual descienda del nivel mínimo aceptado o cuando un lote esté próximo a vencer.
- [x] Desarrollar formulario para generar nuevas solicitudes de compra de insumos a proveedores.
- [x] Diseñar panel de seguimiento de estados de las solicitudes de compra.

#### 📊 Submódulo Gerencia (Dirección e Indicadores)
- [x] Desarrollar bandeja de solicitudes de compra pendientes de revisión (`/manager/requests`).
- [x] Implementar acciones para aprobar o rechazar/cancelar solicitudes de compra con registro de justificación.
- [x] Diseñar el Tablero Gerencial interactivo (`/manager/dashboard`) que presente indicadores en tiempo real de facturación, citas y pacientes.
- [x] Implementar gráficas dinámicas de ingresos (`RevenueChart`) integradas con ChartJS.
- [ ] Implementar la herramienta de generación y exportación de reportes operativos por rangos de fecha seleccionados.

### 🧪 Pruebas a Realizar (QA & Verificación)
- [x] **Prueba de Consumo FIFO de Medicamentos:**
  - *Procedimiento:* Registrar dos lotes del insumo *"Amoxicilina 500mg"*:
    * Lote A: 50 unidades (vence en 10 días).
    * Lote B: 100 unidades (vence en 30 días).
    * Consumir 60 unidades a través del endpoint `/api/v1/stock/consume/`.
  - *Resultado esperado:* El sistema consume primero las 50 unidades del Lote A (por vencer primero) y las 10 unidades restantes del Lote B. El stock remanente del Lote A queda en 0 y el Lote B en 90.
- [x] **Prueba de Alertas de Stock y Vencimiento:**
  - *Procedimiento:* Registrar un lote con stock por debajo del límite mínimo definido para el insumo, y otro lote con fecha de expiración menor a 45 días.
  - *Resultado esperado:* Al ingresar al dashboard de alertas (`InventoryAlertsView`), se deben visualizar alertas de severidad `critical` o `warning` según corresponda.
- [x] **Prueba del Flujo de Compra (Requisición -> Aprobación -> Ingreso de Lote):**
  - *Procedimiento:*
    1. El Técnico genera una solicitud de reabastecimiento por 100 guantes de látex.
    2. La solicitud entra en estado `REQUESTED`.
    3. El Gerente visualiza la solicitud en su panel y hace clic en *"Aprobar"*, transicionando el estado a `APPROVED`.
    4. El Técnico recibe la mercadería físicamente, registrando el número de lote y cantidad real recibida en el sistema.
  - *Resultado esperado:* La orden pasa a estado `RECEIVED`, y el sistema crea automáticamente el nuevo `SupplyBatch` (lote) sumando las existencias al stock activo de la clínica.
- [x] **Prueba de Actualización de KPI en Tablero Gerencial:**
  - *Procedimiento:* Realizar transacciones de cobro / citas exitosas y navegar al Tablero Gerencial.
  - *Resultado esperado:* Los KPI de ingresos totales y volumen se recalculan dinámicamente según el período de tiempo seleccionado (*Hoy*, *Esta Semana*, *Este Mes*).
- [ ] **Prueba de Exportación de Reportes:**
  - *Procedimiento:* Solicitar la generación de un reporte de operaciones del mes anterior y presionar el botón de exportación.
  - *Resultado esperado:* El sistema genera y descarga un archivo estructurado (PDF/Excel) con el desglose correspondiente de actividades.
