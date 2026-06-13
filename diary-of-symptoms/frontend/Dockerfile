FROM node:20-alpine AS build

WORKDIR /app

# Сначала только манифесты, чтобы Docker лучше кешировал слой с зависимостями.
COPY package.json package-lock.json ./

# npm ci ставит ровно то, что зафиксировано в lock-файле.
RUN npm ci

# Если нужен другой API URL, его можно передать при сборке:
# docker build --build-arg VITE_API_BASE_URL=https://api.example.com .
ARG VITE_API_BASE_URL=
# Build-time injected API base. Default is empty string (relative requests).
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}


COPY . .
RUN npm run build

FROM nginx:1.27-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
