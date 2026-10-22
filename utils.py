"""Path helpers that work both from source and from a PyInstaller bundle.

Two kinds of paths exist in a frozen app:

* **Bundle paths** - read-only files that ship inside the exe (the YOLO model,
  the EasyOCR weights, the default settings). They live in the temporary
  extraction folder PyInstaller creates (``sys._MEIPASS``) and disappear when
  the process exits.
* **User paths** - files the app writes (settings.json, logs, screenshots).
  They must live somewhere that survives a restart, so in a frozen app they
  go to ``%APPDATA%\\COCAutoFarm``.

When running from source both resolve to the project directory, so the
behaviour is unchanged for development.
"""

import os
import sys

APP_DIR_NAME = "COCAutoFarm"


def is_frozen() -> bool:
    """True when running from a PyInstaller bundle."""
    return bool(getattr(sys, "frozen", False))


def bundle_dir() -> str:
    """Directory holding the bundled read-only resources.

    In a PyInstaller bundle this is the temporary extraction folder; from
    source it is the directory holding this file.
    """
    if is_frozen():
        return getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


def user_data_dir() -> str:
    """Writable directory for settings, logs and screenshots.

    In a PyInstaller bundle this is ``%APPDATA%\\COCAutoFarm`` so that the
    bot and the calibration tool (which live in different folders) always
    share the same settings. From source it is the project directory.
    """
    if is_frozen():
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
        path = os.path.join(base, APP_DIR_NAME)
    else:
        path = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(path, exist_ok=True)
    return path


def resource_path(relative_path: str) -> str:
    """
    Get absolute path to a bundled (read-only) resource.
    Works both when running from source and when bundled with PyInstaller.
    """
    return os.path.join(bundle_dir(), relative_path)


def user_path(relative_path: str) -> str:
    """
    Get absolute path to a writable user file (settings, logs, screenshots).
    The parent directory is created if it does not exist yet.
    """
    path = os.path.join(user_data_dir(), relative_path)
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    return path


def configure_runtime_env():
    """
    Environment tweaks that the packaged build needs.

    Ultralytics is written to run from a normal Python install: when a
    dependency is missing it runs ``pip install`` on the spot, and it checks
    dependency versions on every start. Neither works inside a frozen app
    (there is no pip, and the "packages" live in the bundle), so both are
    switched off. Must run before ultralytics is imported.
    """
    os.environ.setdefault("YOLO_AUTOINSTALL", "False")
    os.environ.setdefault("ULTRALYTICS_SKIP_REQUIREMENTS_CHECKS", "True")
    if is_frozen():
        os.environ.setdefault("YOLO_CONFIG_DIR", user_data_dir())
