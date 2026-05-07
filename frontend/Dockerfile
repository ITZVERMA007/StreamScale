FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./

RUN npm ci

COPY . .

# Build with production environment
ENV NODE_ENV=production
RUN npm run build

# Serve with a lightweight static server (optional)
FROM node:18-alpine

WORKDIR /app

# Install serve for static hosting
RUN npm install -g serve

COPY --from=builder /app/dist ./dist

EXPOSE 3000

CMD ["serve", "-s", "dist", "-l", "3000"]
