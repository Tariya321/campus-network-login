#!/usr/bin/env python3
"""Run the campus-login script once whenever an outage is detected."""

import argparse
import fcntl
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
import signal
import subprocess
import sys
from threading import Event
from typing import Optional, Tuple

import requests


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR
DEFAULT_LOGIN_SCRIPT = PROJECT_DIR / "WanLoginer.py"
DEFAULT_LOG_FILE = SCRIPT_DIR / "logs" / "network-watchdog.log"
CHECK_HEADERS = {"User-Agent": "campus-login-watchdog/1.0"}
STOP_EVENT = Event()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run WanLoginer once for each detected internet outage."
    )
    parser.add_argument(
        "--login-script",
        type=Path,
        default=DEFAULT_LOGIN_SCRIPT,
        help=f"path to WanLoginer.py (default: {DEFAULT_LOGIN_SCRIPT})",
    )
    parser.add_argument(
        "--check-url",
        default="https://www.baidu.com",
        help="URL used to determine whether the internet is reachable",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=30,
        help="seconds between checks (default: 30)",
    )
    parser.add_argument(
        "--failure-threshold",
        type=int,
        default=2,
        help="consecutive failed checks before login (default: 2)",
    )
    parser.add_argument(
        "--check-timeout",
        type=float,
        default=8,
        help="seconds allowed for one reachability check (default: 8)",
    )
    parser.add_argument(
        "--login-timeout",
        type=float,
        default=600,
        help="maximum seconds allowed for one WanLoginer run (default: 600)",
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        default=DEFAULT_LOG_FILE,
        help=f"log file path (default: {DEFAULT_LOG_FILE})",
    )
    args = parser.parse_args()
    if args.interval <= 0 or args.failure_threshold < 1:
        parser.error("--interval must be positive and --failure-threshold must be at least 1")
    if args.check_timeout <= 0 or args.login_timeout <= 0:
        parser.error("timeouts must be positive")
    return args


def configure_logging(log_file: Path) -> logging.Logger:
    log_file.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("network_watchdog")
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

    file_handler = RotatingFileHandler(
        log_file, maxBytes=1_000_000, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.handlers.clear()
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger


def is_online(check_url: str, timeout: float) -> Tuple[bool, Optional[str]]:
    try:
        response = requests.get(check_url, headers=CHECK_HEADERS, timeout=timeout)
        if response.status_code < 400:
            return True, None
        return False, f"HTTP {response.status_code} from {check_url}"
    except requests.RequestException as error:
        return False, str(error)


def run_login(login_script: Path, timeout: float, logger: logging.Logger) -> bool:
    """Run one complete login invocation and write its output to the watchdog log."""
    try:
        result = subprocess.run(
            [sys.executable, str(login_script)],
            cwd=login_script.parent,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        logger.error("WanLoginer timed out after %.0f seconds", timeout)
        return False
    except OSError as error:
        logger.error("Could not start WanLoginer: %s", error)
        return False

    for line in result.stdout.splitlines():
        logger.info("[WanLoginer] %s", line)
    if result.returncode == 0:
        logger.info("WanLoginer completed successfully")
        return True

    logger.warning("WanLoginer exited with status %s", result.returncode)
    return False


def acquire_lock(lock_path: Path, logger: logging.Logger):
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock_file = lock_path.open("w", encoding="utf-8")
    try:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        logger.error("Another watchdog process is already running; exiting")
        lock_file.close()
        return None
    lock_file.write(f"{os.getpid()}\n")
    lock_file.flush()
    return lock_file


def stop_handler(_signum, _frame) -> None:
    STOP_EVENT.set()


def main() -> int:
    args = parse_args()
    logger = configure_logging(args.log_file)
    login_script = args.login_script.resolve()
    if not login_script.is_file():
        logger.error("Login script does not exist: %s", login_script)
        return 2

    lock_file = acquire_lock(args.log_file.parent / ".network-watchdog.lock", logger)
    if lock_file is None:
        return 0

    signal.signal(signal.SIGINT, stop_handler)
    signal.signal(signal.SIGTERM, stop_handler)
    logger.info(
        "Watchdog started: interval=%ss, threshold=%s, check_url=%s",
        args.interval,
        args.failure_threshold,
        args.check_url,
    )

    consecutive_failures = 0
    login_attempted_for_outage = False
    try:
        while not STOP_EVENT.is_set():
            online, reason = is_online(args.check_url, args.check_timeout)
            if online:
                if consecutive_failures:
                    logger.info("Internet recovered; watchdog re-armed")
                consecutive_failures = 0
                login_attempted_for_outage = False
            else:
                consecutive_failures += 1
                logger.warning(
                    "Reachability check failed (%s/%s): %s",
                    consecutive_failures,
                    args.failure_threshold,
                    reason,
                )
                if (
                    consecutive_failures >= args.failure_threshold
                    and not login_attempted_for_outage
                ):
                    login_attempted_for_outage = True
                    logger.warning("Outage confirmed; starting one WanLoginer run")
                    run_login(login_script, args.login_timeout, logger)

            STOP_EVENT.wait(args.interval)
    finally:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
        lock_file.close()
        logger.info("Watchdog stopped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
