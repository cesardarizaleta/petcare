import json

path = r"c:\Users\Cesar\Desktop\Code\Petcare\CLINICA COMPLETA_2026-05-24T17_28_24.660Z (1).json"
with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Total de tablas: {len(data['tables'])}")
for t in data['tables']:
    fields = [field['name'] for field in t['fields']]
    print(f"- {t['name']}: {', '.join(fields)}")
