FROM node:18

RUN apt-get update -y
RUN apt-get install -y npm
RUN npm install -g nodemon

WORKDIR /app
COPY package.json ./
RUN npm install
COPY index.js ./
CMD ["nodemon", "--legacy-watch","--exec", "node","index.js"]