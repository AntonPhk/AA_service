#!/bin/bash
# update db according last alembic commit
alembic upgrade head

# Start FastAPI app
uvicorn src.main:app --host 0.0.0.0 --port 8000