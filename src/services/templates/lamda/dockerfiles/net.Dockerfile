# Stage 1: Build the application
FROM public.ecr.aws/lambda/dotnet:8 AS build
WORKDIR /app
COPY *.csproj ./
RUN dotnet restore
COPY . ./
RUN dotnet publish -c Release -o /app/publish

# Stage 2: Create final image
FROM public.ecr.aws/lambda/dotnet:8
WORKDIR /var/task
COPY --from=build /app/publish ./

CMD [ "Lambda::Lambda.Function::FunctionHandler" ]

