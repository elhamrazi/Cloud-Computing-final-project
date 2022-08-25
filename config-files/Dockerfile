FROM python:3.7-slim AS compile-image

# Make sure we use the virtualenv:
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .


FROM python:3.7-alpine AS build-image

WORKDIR /app/
COPY --from=compile-image /app /app
RUN pip install -r requirements.txt

CMD ["python3", "app.py"]