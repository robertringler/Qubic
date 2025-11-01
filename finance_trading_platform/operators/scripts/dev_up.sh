#!/usr/bin/env bash
set -e
python -m venv .venv
source .venv/bin/activate
pip install -r ../services/backend/requirements.txt
python ../services/backend/app.py
