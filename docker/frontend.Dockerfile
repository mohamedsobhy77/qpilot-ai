# docker/frontend.Dockerfile
# Next.js frontend with hot reload for development

FROM node:20-alpine

WORKDIR /app

# Install dependencies first (better layer caching)
COPY package.json ./
RUN npm install
# Copy source
COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
