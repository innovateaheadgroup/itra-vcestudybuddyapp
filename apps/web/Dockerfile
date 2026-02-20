FROM node:22-alpine

WORKDIR /app

COPY package.json /app/package.json
COPY apps/web/package.json /app/apps/web/package.json
COPY packages/shared/package.json /app/packages/shared/package.json
RUN npm install

COPY apps/web /app/apps/web
COPY packages/shared /app/packages/shared

WORKDIR /app/apps/web

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]
