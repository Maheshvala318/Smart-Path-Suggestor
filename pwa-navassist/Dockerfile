version: '3'
services:
  navassist-nav:
    image: node:20-alpine
    working_dir: /app
    volumes:
      - ./:/app
    command: sh -c "npm install && npm run build && npm start"
    ports:
      - "5173:5173"
    environment:
      - NODE_ENV=production
