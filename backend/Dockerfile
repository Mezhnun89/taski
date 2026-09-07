FROM python:3.10-alpine AS dependencies
WORKDIR /code
COPY requirements.txt .
RUN pip install --no-cache-dir --target=/dependencies -r requirements.txt

FROM python:3.10-alpine AS runtime
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /code
COPY --from=dependencies /dependencies /usr/local/lib/python3.10/site-packages
COPY . .
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
