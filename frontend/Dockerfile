# build-stage
FROM node:18 AS build-stage

# Add build argument with a default value
ARG API_BASE_URL=http://localhost:8088

# Set it as an environment variable
ENV API_BASE_URL=$API_BASE_URL

RUN echo "the API_BASE_URL is: $API_BASE_URL"

# set working directory
WORKDIR /app

# ensure using specific npm version
RUN npm install -g npm@8.6.0

# Install nasm and gawk
RUN apt-get update && apt-get install -y gnupg2 && \
    apt-get install -y nasm gawk

RUN apt-get install -y curl

# copy package.json and package-lock.json
COPY package*.json ./

# set npm registry to use mirror if you can't download librayies
# RUN npm config set registry https://registry.npmmirror.com/

# install project dependencies
RUN npm install

# copy project files
COPY . .

# build app
RUN npm run build

# build-stage -> production-stage
FROM node:18 AS production-stage

# set working directory
WORKDIR /app

# copy build files from build stage
COPY --from=build-stage /app/dist ./dist

# copy package files
COPY --from=build-stage /app/package*.json ./

# install only production dependencies and skip prepare script
RUN npm pkg delete scripts.prepare && npm install --only=production

# install serve package globally
RUN npm install -g serve

# expose port
EXPOSE 3000

# start server
CMD ["serve", "-s", "dist", "-l", "3000"]