FROM python:3.10-slim
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
COPY . .
ENV JAX_PLATFORM_NAME=cpu
EXPOSE 8000
CMD ["gunicorn", "-b", "0.0.0.0:8000", "-w", "4", "app:app"]
