#!/bin/bash
# update db according last alembic commit
alembic -c alembic.ini upgrade head

# Start FastAPI app
uvicorn src.main:app --host 0.0.0.0 --port 8001