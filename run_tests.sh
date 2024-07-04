_#!/bin/bash
export PYTHONPATH=./
rm -rf db.sqlite3
make migrate
pytest