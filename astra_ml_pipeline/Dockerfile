FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Run forecast bridge in loop mode
CMD ["python", "-u", "run_forecast.py", "--loop"]
