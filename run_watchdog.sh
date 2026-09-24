#!/bin/sh
# Start the watcher with this repository's virtual environment when available.
set -eu

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

if [ -n "${PYTHON_BIN:-}" ]; then
    python_bin=$PYTHON_BIN
elif [ -x "$script_dir/.venv/bin/python" ]; then
    python_bin=$script_dir/.venv/bin/python
else
    python_bin=python3
fi

exec "$python_bin" "$script_dir/network_watchdog.py" "$@"
