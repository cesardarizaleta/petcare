#!/usr/bin/env python
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def reset_db():
    print("Iniciando reseteo de base de datos local...")
    db_file = BASE_DIR / 'db.sqlite3'
    if db_file.exists():
        print(f"Eliminando base de datos SQLite existente en {db_file}...")
        try:
            os.remove(db_file)
            print("Base de datos SQLite eliminada con éxito.")
        except Exception as e:
            print(f"Error al eliminar la base de datos: {e}")
            sys.exit(1)
    else:
        print("No se encontró base de datos SQLite existente (se creará una nueva).")

if __name__ == '__main__':
    reset_db()
