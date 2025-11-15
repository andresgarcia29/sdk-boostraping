# Stage 1: Build dependencies
FROM public.ecr.aws/lambda/python:3.11 AS build
WORKDIR /app
COPY requirements.txt ./
RUN pip install --target /app/python -r requirements.txt

# Stage 2: Create final image
FROM public.ecr.aws/lambda/python:3.11
WORKDIR /var/task
COPY --from=build /app/python ./python
COPY index.py ./

CMD [ "index.handler" ]

