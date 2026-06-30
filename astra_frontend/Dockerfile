# Stage 1: Build stage
FROM node:20-alpine AS build

WORKDIR /app

# Copy package descriptors and lockfile
COPY package*.json ./

# Install packages
RUN npm ci

# Copy the rest of the frontend source
COPY . .

# Injected at build time by Docker Compose or Render
ARG VITE_API_BASE
ENV VITE_API_BASE=$VITE_API_BASE

# Build Vite application
RUN npm run build

# Stage 2: Web Server Stage
FROM nginx:alpine

# Copy built files from the build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Setup fallback Nginx rule for SPA routes
RUN echo 'server { \
    listen 80; \
    location / { \
        root /usr/share/nginx/html; \
        index index.html index.htm; \
        try_files $uri $uri/ /index.html; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
