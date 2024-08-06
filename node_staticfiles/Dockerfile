FROM node:18.14.0-bullseye-slim

# Create app directory
WORKDIR /node

# Install app dependencies
# A wildcard is used to ensure both package.json AND package-lock.json are copied
# where available (npm@5+)
# COPY package.json package.json 
# COPY package-lock.json package-lock.json

COPY . .

RUN npm install
# RUN mkdir /home/project
# If you are building your code for production
# RUN npm ci --only=production

# ENTRYPOINT [ "npm", "run", "dev" ] 