#!/bin/bash
# Skrypt do uruchomienia aplikacji

cd "$(dirname "$0")"
source venv/bin/activate
python app.py

