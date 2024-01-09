FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY src .
RUN curl https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css > /app/static/bootstrap.css && \
    curl https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js > /app/static/bootstrap.js

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]