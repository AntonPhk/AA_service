#!/bin/bash
# update db according last alembic commit
alembic -c alembic.ini upgrade head

# Create default roles and permissions
python -m scripts.db_default_tables_values

# Start FastAPI app
uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload