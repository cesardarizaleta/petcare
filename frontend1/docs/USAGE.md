# Guía de uso — Plantilla SDK-Frontend

Esta guía describe cómo usar esta plantilla para seguir desarrollando la aplicación, las convenciones y ejemplos de uso (incluyendo `axios`).

## Resumen

Proyecto Vue 3 con Vite, Pinia, Vue Router y una estructura pensada para aplicaciones tipo panel/SPA.

## Requisitos

- Node.js (recomendado 16+)
- npm (o pnpm/yarn según prefieras)

## Instalación inicial

1. Clona el repositorio.
2. Instala dependencias:

```bash
npm install
```

3. Arranca en modo desarrollo:

```bash
npm run dev
```

## Scripts útiles

- `npm run dev` — arranca Vite en modo desarrollo
- `npm run build` — construye la app para producción
- `npm run preview` — sirve la build localmente
- `npm run format` — formatea el código con Prettier
- `npm run format:check` — comprueba formato sin modificar archivos

## Formato y editor

Se incluye Prettier con la configuración en `.prettierrc` y `.prettierignore`. En `.vscode/settings.json` está configurado Prettier como formateador por defecto y `formatOnSave` activado.

## Estructura del proyecto (resumen)

- `src/components/` — componentes reutilizables
- `src/layout/` — componentes de layout (Sidebar, AppLayout)
- `src/shared/` — componentes compartidos de UI
- `src/views/` — vistas por rol/feature
- `src/stores/` — stores de Pinia
- `src/router/` — rutas de la aplicación
- `src/lib/` — utilidades y librerías (aquí colocamos el wrapper de `axios`)

## Uso de `axios` (instalado aquí)

He añadido un wrapper base en [src/lib/http.js](src/lib/http.js) que exporta una instancia de `axios` preconfigurada.

### Configuración de la base URL

Usa la variable de entorno `VITE_API_BASE_URL`. Crea un archivo `.env` en la raíz con:

```
VITE_API_BASE_URL=https://api.tudominio.com
```

Vite expondrá esta variable en tiempo de ejecución (prefijo `VITE_`).

### Ejemplo de uso (componente o composable)

```js
import http from '../lib/http.js';

export async function fetchPets() {
  const res = await http.get('/pets');
  return res.data;
}
```

### Manejo de tokens

El wrapper añade espacio para añadir un token (ejemplo en `localStorage`) en los interceptores. Ajusta según tu estrategia de autenticación.

## Buenas prácticas para seguir programando

- Crea ramas por feature (`feature/mi-nueva-pantalla`).
- Ejecuta `npm run format` antes de commitear.
- Añade tests o validación mínima para nuevas funciones.
- Mantén componentes pequeños y separados entre `shared/` y `views/`.

## Siguientes pasos recomendados

- Añadir `husky` + `lint-staged` para formateo y checks pre-commit (puedo configurarlo si quieres).
- Añadir ESLint si deseas comprobación adicional de calidad de código.

---

Si quieres, actualizo el `README.md` principal con un enlace a esta guía y/o configuro `husky` + `lint-staged` para formatear antes de commits.
