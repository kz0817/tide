FROM debian:12

RUN apt-get update && apt-get install -y \
  python3 \
  npm

RUN npm install -g typescript
