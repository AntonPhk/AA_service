FROM python:3.11.9-alpine as builder
LABEL authors="antonphk"

WORKDIR /tmp

# Install poetry
RUN python -m pip install poetry==1.8.2

# Copy poetry files
COPY pyproject.toml poetry.lock ./


# Install dependencies using poetry
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes


# Stage 2: Runtime stage
FROM python:3.11.9-alpine


WORKDIR /app

# Disable of saving .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Add new user
RUN adduser -D myuser && chown -R myuser /app


# Copy project files from the builder stage
COPY --from=builder /tmp/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

# Copying project files
COPY . .

# Change to safety role
USER myuser

# Set the command to run your application
ENTRYPOINT ["sh", "entrypoint.sh"]
