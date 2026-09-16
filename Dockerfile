FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY halluguard ./halluguard
RUN pip install --no-cache-dir .
EXPOSE 8000
CMD ["uvicorn","halluguard.api:app","--host","0.0.0.0","--port","8000"]
