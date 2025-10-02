# Etapa 1: Build do frontend
FROM node:20-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .

# Usa a env passada pelo docker-compose
ARG VUE_APP_API_URL
ENV VUE_APP_API_URL=$VUE_APP_API_URL

RUN npm run build

# Etapa 2: Servir com Nginx
FROM nginx:alpine

# Copia o build para o nginx
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
