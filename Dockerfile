FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install poetry
RUN pip install --no-cache-dir poetry

# Copy project files
COPY pyproject.toml poetry.lock* README.md ./

# Install dependencies (use poetry inside docker)
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Copy the actual application code
COPY . .

# Expose port
EXPOSE 8000

# Run the server
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
