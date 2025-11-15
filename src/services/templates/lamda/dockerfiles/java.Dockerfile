# Stage 1: Build the application
FROM public.ecr.aws/lambda/java:17 AS build
WORKDIR /app
COPY pom.xml ./
RUN mvn dependency:go-offline -B
COPY src ./src
RUN mvn package -DskipTests

# Stage 2: Create final image
FROM public.ecr.aws/lambda/java:17
WORKDIR /var/task
COPY --from=build /app/target/*.jar ./

CMD [ "com.example.Handler::handleRequest" ]

