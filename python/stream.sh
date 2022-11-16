#! /bin/bash
source ../venv/bin/activate
faust -A stream worker -l info
