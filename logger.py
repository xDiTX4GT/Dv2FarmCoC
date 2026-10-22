import logging
import os
import sys

from utils import user_path


def setup_logging(level=logging.INFO):
    """
    Setup root logger with file + console output.
    Logs are written to <user data dir>/logs/bot.log (the project directory
    when running from source, %APPDATA%\\COCAutoFarm\\logs when bundled).

    Level routing: the console handler shows ``level`` (default INFO) and up,
    while ``logs/bot.log`` keeps DEBUG and up — so per-tap audit detail
    (bot sweep clicks) reaches the file without flooding the console/GUI.
    """
    log_dir = user_path("logs")
    os.makedirs(log_dir, exist_ok=True)

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S"
    )

    fh = logging.FileHandler(
        os.path.join(log_dir, "bot.log"),
        encoding="utf-8"
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(level)
    ch.setFormatter(formatter)

    root = logging.getLogger()
    # Root must be at least as permissive as the most verbose handler,
    # otherwise DEBUG entries are filtered before reaching the file.
    root.setLevel(logging.DEBUG)
    # avoid duplicate handlers if called multiple times
    if not root.handlers:
        root.addHandler(fh)
        root.addHandler(ch)
