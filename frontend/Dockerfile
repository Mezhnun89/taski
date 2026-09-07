# Учебный dev-server, версия Node из примера урока.
FROM node:16.14.0-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
# localhost внутри frontend-контейнера не является backend-контейнером.
RUN npm pkg set proxy=http://taski-backend:8000
ENV HOST=0.0.0.0
EXPOSE 3000
CMD ["npm", "start"]
