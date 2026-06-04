# Reporte de Pruebas Unitarias del Backend

Este documento detalla todas las pruebas unitarias implementadas en el backend de Django, ejecutadas y verificadas con éxito.

### Resumen de Ejecución
- **Total de Pruebas Ejecutadas:** 74
- **Estado General:** **OK** (100% Exitosas)
- **Tiempo de Ejecución:** ~8.16 segundos

--- 

## Módulo `appointments`
Ubicación del archivo: [tests.py](file:///c:/Users/Cesar/Desktop/Code/Petcare/backend/apps/appointments/tests.py)

| Clase de Prueba | Método de Prueba | Descripción | Estado |
| :--- | :--- | :--- | :--- |
| `AppointmentsTestCase` | `test_vet_slots_retrieval_and_autocreate` | Verificación del comportamiento esperado. | **PASSED** ✅ |
| `AppointmentsTestCase` | `test_schedule_calendar` | Verificación del comportamiento esperado. | **PASSED** ✅ |
| `AppointmentsTestCase` | `test_appointment_booking_and_cancellation_flow` | Verificación del comportamiento esperado. | **PASSED** ✅ |
| `AppointmentsTestCase` | `test_check_in_and_waiting_list` | Verificación del comportamiento esperado. | **PASSED** ✅ |
| `AppointmentsTestCase` | `test_appointment_consultation_creation` | Verificación del comportamiento esperado. | **PASSED** ✅ |
| `AppointmentsTestCase` | `test_appointment_consultation_invalid_weight` | Verificación del comportamiento esperado. | **PASSED** ✅ |
| `AppointmentsTestCase` | `test_appointment_consultation_invalid_temperature` | Verificación del comportamiento esperado. | **PASSED** ✅ |
| `AppointmentsTestCase` | `test_rebook_cancelled_slot` | Verificación del comportamiento esperado. | **PASSED** ✅ |


## Módulo `notifications`
Ubicación del archivo: [tests.py](file:///c:/Users/Cesar/Desktop/Code/Petcare/backend/apps/notifications/tests.py)

| Clase de Prueba | Método de Prueba | Descripción | Estado |
| :--- | :--- | :--- | :--- |
| `NotificationsTestCase` | `test_notifications_list` | Verificación del comportamiento esperado. | **PASSED** ✅ |
| `NotificationsTestCase` | `test_notification_read` | Verificación del comportamiento esperado. | **PASSED** ✅ |
| `NotificationsTestCase` | `test_notification_read_all` | Verificación del comportamiento esperado. | **PASSED** ✅ |


## Módulo `owners`
Ubicación del archivo: [tests.py](file:///c:/Users/Cesar/Desktop/Code/Petcare/backend/apps/owners/tests.py)

| Clase de Prueba | Método de Prueba | Descripción | Estado |
| :--- | :--- | :--- | :--- |
| `OwnerAppTests` | `test_get_owner_me` | Verificación del comportamiento esperado. | **PASSED** ✅ |
| `OwnerAppTests` | `test_patch_owner_me` | Verificación del comportamiento esperado. | **PASSED** ✅ |
| `OwnerAppTests` | `test_patch_owner_me_invalid_phone` | Verificación del comportamiento esperado. | **PASSED** ✅ |
| `OwnerAppTests` | `test_owner_me_pets_flow` | Verificación del comportamiento esperado. | **PASSED** ✅ |
| `OwnerAppTests` | `test_receptionist_views` | Verificación del comportamiento esperado. | **PASSED** ✅ |
| `OwnerAppTests` | `test_permission_protection` | Verificación del comportamiento esperado. | **PASSED** ✅ |


## Módulo `patients`
Ubicación del archivo: [tests.py](file:///c:/Users/Cesar/Desktop/Code/Petcare/backend/apps/patients/tests.py)

| Clase de Prueba | Método de Prueba | Descripción | Estado |
| :--- | :--- | :--- | :--- |
| `PatientsTestCase` | `test_patient_list_api` | Verificación del comportamiento esperado. | **PASSED** ✅ |
| `PatientsTestCase` | `test_patient_detail_and_update` | Verificación del comportamiento esperado. | **PASSED** ✅ |
| `PatientsTestCase` | `test_pet_medical_record_summary` | Verificación del comportamiento esperado. | **PASSED** ✅ |
| `PatientsTestCase` | `test_pet_medical_record_full` | Verificación del comportamiento esperado. | **PASSED** ✅ |
| `PatientsTestCase` | `test_vaccination_schedule_and_register_event` | Verificación del comportamiento esperado. | **PASSED** ✅ |
| `PatientsTestCase` | `test_vaccination_event_future_applied_date` | Verificación del comportamiento esperado. | **PASSED** ✅ |
| `PatientsTestCase` | `test_vaccination_event_past_next_due_date` | Verificación del comportamiento esperado. | **PASSED** ✅ |


## Módulo `reporting`
Ubicación del archivo: [tests.py](file:///c:/Users/Cesar/Desktop/Code/Petcare/backend/apps/reporting/tests.py)

| Clase de Prueba | Método de Prueba | Descripción | Estado |
| :--- | :--- | :--- | :--- |
| `ReportingTestCase` | `test_unauthenticated_fails` | Verify endpoints are protected by default authentication. | **PASSED** ✅ |
| `ReportingTestCase` | `test_dashboard_summary_calculation` | Verify the KPI numbers and revenue graph calculations are correct. | **PASSED** ✅ |
| `ReportingTestCase` | `test_kpi_list_endpoint` | Verify the dedicated KPI list endpoint returns the expected array. | **PASSED** ✅ |
| `ReportingTestCase` | `test_revenue_chart_endpoint` | Verify the revenue endpoint works and yields correct date points. | **PASSED** ✅ |
| `ReportingTestCase` | `test_export_report_csv` | Verify CSV reporting format generation and content headers. | **PASSED** ✅ |
| `ReportingTestCase` | `test_export_report_json` | Verify JSON reporting format generation and payload fields. | **PASSED** ✅ |
| `ReportingTestCase` | `test_custom_date_range` | Verify custom date ranges via 'from' and 'to' query parameters work correctly. | **PASSED** ✅ |


## Módulo `tests`
Ubicación del archivo: [test_inventory.py](file:///c:/Users/Cesar/Desktop/Code/Petcare/backend/apps/stock/tests/test_inventory.py)

| Clase de Prueba | Método de Prueba | Descripción | Estado |
| :--- | :--- | :--- | :--- |
| `BatchCreationTestCase` | `test_create_batch_success` | Prueba que se pueda registrar un lote correctamente | **PASSED** ✅ |
| `BatchCreationTestCase` | `test_create_batch_invalid_supply` | Prueba que falle si el insumo no existe | **PASSED** ✅ |
| `AlertsTestCase` | `test_low_stock_critical_alert` | Prueba que el endpoint de alertas detecte stock crítico | **PASSED** ✅ |
| `ConsumeFIFOServiceTestCase` | `test_consume_from_first_batch` | Verificación del comportamiento esperado. | **PASSED** ✅ |
| `ConsumeFIFOServiceTestCase` | `test_consume_spanning_two_batches` | Verificación del comportamiento esperado. | **PASSED** ✅ |
| `ConsumeFIFOServiceTestCase` | `test_consume_spanning_three_batches` | Verificación del comportamiento esperado. | **PASSED** ✅ |
| `ConsumeFIFOServiceTestCase` | `test_consume_exact_total` | Verificación del comportamiento esperado. | **PASSED** ✅ |
| `ConsumeFIFOServiceTestCase` | `test_consume_exceeds_stock_raises_error` | Verificación del comportamiento esperado. | **PASSED** ✅ |
| `ConsumeFIFOServiceTestCase` | `test_consume_zero_raises_error` | Verificación del comportamiento esperado. | **PASSED** ✅ |
| `ConsumeFIFOServiceTestCase` | `test_consume_negative_raises_error` | Verificación del comportamiento esperado. | **PASSED** ✅ |
| `ConsumeFIFOServiceTestCase` | `test_nonexistent_supply_raises_error` | Verificación del comportamiento esperado. | **PASSED** ✅ |
| `ConsumeFIFOServiceTestCase` | `test_expired_batches_excluded` | Verificación del comportamiento esperado. | **PASSED** ✅ |
| `ConsumeFIFOServiceTestCase` | `test_consultation_supply_created` | Verificación del comportamiento esperado. | **PASSED** ✅ |
| `ConsumeFIFOServiceTestCase` | `test_no_consultation_supply_without_id` | Verificación del comportamiento esperado. | **PASSED** ✅ |
| `ConsumeEndpointTestCase` | `test_consume_success` | Verificación del comportamiento esperado. | **PASSED** ✅ |
| `ConsumeEndpointTestCase` | `test_consume_with_consultation` | Verificación del comportamiento esperado. | **PASSED** ✅ |
| `ConsumeEndpointTestCase` | `test_consume_insufficient_stock` | Verificación del comportamiento esperado. | **PASSED** ✅ |
| `ConsumeEndpointTestCase` | `test_consume_missing_fields` | Verificación del comportamiento esperado. | **PASSED** ✅ |
| `ConsumeEndpointTestCase` | `test_unauthenticated_rejected` | Verificación del comportamiento esperado. | **PASSED** ✅ |
| `SupplyCreationTestCase` | `test_create_supply_success` | Verificación del comportamiento esperado. | **PASSED** ✅ |


## Módulo `tests`
Ubicación del archivo: [test_orders.py](file:///c:/Users/Cesar/Desktop/Code/Petcare/backend/apps/stock/tests/test_orders.py)

| Clase de Prueba | Método de Prueba | Descripción | Estado |
| :--- | :--- | :--- | :--- |
| `PurchaseOrderServiceTest` | `test_approve_order` | Verificación del comportamiento esperado. | **PASSED** ✅ |
| `PurchaseOrderServiceTest` | `test_approve_non_requested_order_fails` | Verificación del comportamiento esperado. | **PASSED** ✅ |
| `PurchaseOrderServiceTest` | `test_receive_order_creates_batches` | Verificación del comportamiento esperado. | **PASSED** ✅ |
| `PurchaseOrderServiceTest` | `test_receive_non_approved_order_fails` | Verificación del comportamiento esperado. | **PASSED** ✅ |
| `PurchaseOrderServiceTest` | `test_cancel_requested_order` | Verificación del comportamiento esperado. | **PASSED** ✅ |
| `PurchaseOrderServiceTest` | `test_cancel_approved_order` | Verificación del comportamiento esperado. | **PASSED** ✅ |
| `PurchaseOrderServiceTest` | `test_cancel_received_order_fails` | Verificación del comportamiento esperado. | **PASSED** ✅ |
| `PurchaseOrderAPITest` | `test_create_order_from_interface_vue_payload` | Test con el payload exacto que envía Interface.vue. | **PASSED** ✅ |
| `PurchaseOrderAPITest` | `test_create_order_invalid_supplier` | Verificación del comportamiento esperado. | **PASSED** ✅ |
| `PurchaseOrderAPITest` | `test_create_order_empty_items` | Verificación del comportamiento esperado. | **PASSED** ✅ |
| `PurchaseOrderAPITest` | `test_full_workflow` | Test del flujo completo: crear → aprobar → recibir. | **PASSED** ✅ |
| `PurchaseOrderAPITest` | `test_cancel_order` | Verificación del comportamiento esperado. | **PASSED** ✅ |
| `PurchaseOrderAPITest` | `test_filter_by_status` | Verificación del comportamiento esperado. | **PASSED** ✅ |


## Módulo `users`
Ubicación del archivo: [tests.py](file:///c:/Users/Cesar/Desktop/Code/Petcare/backend/apps/users/tests.py)

| Clase de Prueba | Método de Prueba | Descripción | Estado |
| :--- | :--- | :--- | :--- |
| `UsersAuthTestCase` | `test_owner_registration_success` | Verificación del comportamiento esperado. | **PASSED** ✅ |
| `UsersAuthTestCase` | `test_registration_invalid_phone` | Verificación del comportamiento esperado. | **PASSED** ✅ |
| `UsersAuthTestCase` | `test_registration_missing_fields` | Verificación del comportamiento esperado. | **PASSED** ✅ |
| `UsersAuthTestCase` | `test_registration_duplicate_email` | Verificación del comportamiento esperado. | **PASSED** ✅ |
| `UsersAuthTestCase` | `test_login_success` | Verificación del comportamiento esperado. | **PASSED** ✅ |
| `UsersAuthTestCase` | `test_login_invalid_credentials` | Verificación del comportamiento esperado. | **PASSED** ✅ |
| `UsersAuthTestCase` | `test_login_veterinarian_success` | Verificación del comportamiento esperado. | **PASSED** ✅ |
| `UsersAuthTestCase` | `test_login_veterinarian_denied_role` | Verificación del comportamiento esperado. | **PASSED** ✅ |
| `UsersAuthTestCase` | `test_verify_user_authenticated` | Verificación del comportamiento esperado. | **PASSED** ✅ |
| `UsersAuthTestCase` | `test_verify_user_unauthenticated` | Verificación del comportamiento esperado. | **PASSED** ✅ |

