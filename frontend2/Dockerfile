# Etapa 1: Compilar la aplicación de Vue
FROM node:20-alpine AS build-stage

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias
COPY package*.json ./
RUN npm ci

# Copiar código y compilar
COPY . .
# En Dokploy, puedes pasar esta variable de entorno en el build
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
RUN npm run build

# Etapa 2: Servir con Nginx
FROM nginx:alpine AS production-stage

# Eliminar conf por defecto y añadir la nuestra (para Single Page Applications)
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copiar archivos compilados
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Exponer puerto 80 (Dokploy lo detectará)
EXPOSE 80

# Arrancar Nginx
CMD ["nginx", "-g", "daemon off;"]
