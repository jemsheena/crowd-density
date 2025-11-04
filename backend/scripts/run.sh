#!/bin/bash
# Development server runner

export PYTHONPATH="${PYTHONPATH}:$(pwd)"

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

