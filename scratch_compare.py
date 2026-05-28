import os
import sys
import django
import json

# Agregar el directorio backend al path de python
sys.path.append(r"c:\Users\Cesar\Desktop\Code\Petcare\backend")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.apps import apps

# Cargar esquema JSON
path = r"c:\Users\Cesar\Desktop\Code\Petcare\CLINICA COMPLETA_2026-05-24T17_28_24.660Z (1).json"
with open(path, "r", encoding="utf-8") as f:
    schema_data = json.load(f)

print("=== COMPARACIÓN DE MODELOS DJANGO VS ESQUEMA JSON ===")

# Obtener todos los modelos de Django
django_models = {}
for model in apps.get_models():
    db_table = model._meta.db_table
    # Obtener nombres de campos físicos de la base de datos
    fields = {}
    for field in model._meta.get_fields():
        if field.one_to_many or field.many_to_many:
            continue
        # Obtener el nombre de la columna real en la DB
        column = field.column if hasattr(field, 'column') else field.name
        fields[column] = field.get_internal_type()
    django_models[db_table] = {
        'model_name': model.__name__,
        'fields': fields
    }

missing_tables = []
matched_tables = []

for table in schema_data['tables']:
    t_name = table['name']
    
    # Intentar buscar por nombre exacto o nombres comunes en Django (que a veces añade prefijos como appname_tablename)
    found_table = None
    if t_name in django_models:
        found_table = t_name
    else:
        # Buscar por coincidencia parcial (ej. apps_users, users_user, etc.)
        for dj_t in django_models:
            if dj_t.endswith('_' + t_name) or dj_t.endswith(t_name) or t_name.endswith(dj_t) or dj_t.replace('_', '') == t_name.replace('_', ''):
                found_table = dj_t
                break
                
    if not found_table:
        missing_tables.append(t_name)
    else:
        matched_tables.append((t_name, found_table))

print(f"\nTablas encontradas o mapeadas ({len(matched_tables)}):")
for json_t, dj_t in matched_tables:
    print(f"✅ {json_t} -> Mapeada en Django como db_table: '{dj_t}' (Modelo: {django_models[dj_t]['model_name']})")
    # Comparar campos
    json_fields = [f['name'] for f in [t for t in schema_data['tables'] if t['name'] == json_t][0]['fields']]
    dj_fields = list(django_models[dj_t]['fields'].keys())
    
    missing_fields = []
    for jf in json_fields:
        if jf not in dj_fields:
            missing_fields.append(jf)
            
    if missing_fields:
        print(f"   ⚠️ Campos en JSON ausentes en la DB real: {missing_fields}")
    else:
        print(f"   ✨ Todos los campos coinciden.")

print(f"\nTablas en JSON que NO están mapeadas en Django ({len(missing_tables)}):")
for t in missing_tables:
    print(f"❌ {t}")
