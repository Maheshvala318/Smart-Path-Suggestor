FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Create config.js from environment variables at runtime
RUN echo 'window.NAVASSIST_CONFIG = {' > dist/config.js && \
    echo '  GROQ_API_KEY: "",' >> dist/config.js && \
    echo '  DEEPGRAM_API_KEY: "",' >> dist/config.js && \
    echo '  NAVIGATION_SERVER: "",' >> dist/config.js && \
    echo '  DETECTION_SERVER: "",' >> dist/config.js && \
    echo '};' >> dist/config.js

EXPOSE 10000
CMD ["sh", "-c", "echo \"window.NAVASSIST_CONFIG = { GROQ_API_KEY: '$GROQ_API_KEY', DEEPGRAM_API_KEY: '$DEEPGRAM_API_KEY', NAVIGATION_SERVER: '$NAVIGATION_SERVER', DETECTION_SERVER: '$DETECTION_SERVER' };\" > /app/dist/config.js && npm start"]
