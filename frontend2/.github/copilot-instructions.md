# Project Instructions for GitHub Copilot

Este proyecto es un frontend construido en **Vue 3**, **Vite**, **Vue Router** y **Pinia**. Por favor, sigue estas convenciones de código al asistir en la escritura:

1. **Composition API**: Usa SIEMPRE `<script setup>` en Vue. Prohibido usar Options API (`export default { data() ... }`).
2. **Estado Global**: Usa las stores que se encuentran en `src/stores/` mediante Pinia.
3. **Manejo de CSS**: El proyecto prefiere CSS puro apoyado en variables CSS ubicadas en `src/style.css`. Evita proponer Tailwind CSS u otros frameworks a menos que se te pida explícitamente. Las tarjetas y UI tienen bordes predefinidos en variables como `var(--radius-md)`.
4. **Reutilización**: Revisa la carpeta `src/components/` antes de sugerir crear de cero botones, tarjetas, o modales (ahí encontrarás componentes compartidos o de interfaz).
5. **Idioma**: Utiliza español en comentarios, documentación, y para las interacciones en el chat relacionadas a este proyecto.
