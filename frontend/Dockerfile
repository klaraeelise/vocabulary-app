FROM node:20-alpine

WORKDIR /app
COPY . .

RUN npm install

# Start in dev mode with hot reload
CMD ["npm", "run", "dev"]
