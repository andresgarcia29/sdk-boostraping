# Stage 1: Build dependencies
FROM public.ecr.aws/lambda/nodejs:20 AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --omit=dev

# Stage 2: Create final image
FROM public.ecr.aws/lambda/nodejs:20
WORKDIR /var/task
COPY --from=build /app/node_modules ./node_modules
COPY index.js package.json ./

CMD [ "index.handler" ]
