# coding=utf-8
####################################################
# Update Checker
#
# Fetches a small JSON manifest describing the latest release and
# compares it against the running version. Points at our own domain
# rather than a specific hosting platform, same reasoning as the
# donate redirect: existing installs keep working even if where the
# manifest / downloads are hosted changes.
#
# Author: Tobias Grupe
####################################################

import json
import platform
import re
import urllib.error
import urllib.request

MANIFEST_URL = 'http://liveworks-vt.de/downloads/dlive-midi-tools/latest.json'

# Highest manifest_version this app build knows how to read. Bump this
# (and add handling for it) when the manifest shape changes; old app
# installs then recognize a newer manifest_version and can fail
# gracefully instead of misreading fields that changed meaning.
SUPPORTED_MANIFEST_VERSION = 1

# Expected manifest shape:
# {
#   "manifest_version": 1,
#   "version": "2.14.0",
#   "release_notes_url": "https://...",
#   "downloads": {
#     "macos-arm64": "https://...",
#     "macos-x86_64": "https://...",
#     "windows-x86_64": "https://..."
#   }
# }


def _parse_version(version_string):
    """Extract a comparable (major, minor, patch) tuple, ignoring any
    pre-release suffix like '-RC2'."""
    match = re.match(r'(\d+)\.(\d+)\.(\d+)', version_string or '')
    if not match:
        return 0, 0, 0
    return tuple(int(part) for part in match.groups())


def is_update_available(latest_version, current_version):
    return _parse_version(latest_version) > _parse_version(current_version)


def current_platform_key():
    system = platform.system()
    machine = platform.machine().lower()

    if system == "Darwin":
        return "macos-arm64" if machine in ("arm64", "aarch64") else "macos-x86_64"
    if system == "Windows":
        return "windows-x86_64"
    return None


def get_download_url_for_platform(downloads):
    return (downloads or {}).get(current_platform_key())


def fetch_latest_release_info(timeout=5):
    """Fetch and parse the update manifest. Raises on any network / format
    error, or if the manifest is a newer format than this build understands."""
    req = urllib.request.Request(MANIFEST_URL, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as response:
        info = json.loads(response.read())

    manifest_version = info.get("manifest_version", 1)
    if manifest_version > SUPPORTED_MANIFEST_VERSION:
        raise ValueError(
            f"Update manifest format (v{manifest_version}) is newer than this "
            f"app version supports (v{SUPPORTED_MANIFEST_VERSION}). Please "
            f"download the latest version manually.")

    return info
