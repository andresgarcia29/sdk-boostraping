# Stage 1: Build the application
FROM public.ecr.aws/lambda/go:1 AS build
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY main.go ./
RUN go build -o bootstrap main.go

# Stage 2: Create final image
FROM public.ecr.aws/lambda/go:1
WORKDIR /var/task
COPY --from=build /app/bootstrap ./

CMD [ "bootstrap" ]

