from __future__ import annotations

import json


class _Response:
    def __init__(self, payload):
        self._payload = payload

    def read(self):
        return json.dumps(self._payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False


def test_is_newer_version_compares_numeric_segments():
    from updates import is_newer_version

    assert is_newer_version("v1.0.12", "1.0.9") is True
    assert is_newer_version("1.0.0", "1.0.0") is False
    assert is_newer_version("not-a-version", "1.0.0") is False


def test_check_for_update_returns_newer_release():
    from updates import check_for_update

    info = check_for_update(
        current_version="1.0.2",
        opener=lambda *_args, **_kwargs: _Response({
            "tag_name": "v1.0.3",
            "html_url": "https://example.test/releases/v1.0.3",
        }),
    )

    assert info is not None
    assert info.version == "1.0.3"
    assert info.url == "https://example.test/releases/v1.0.3"


def test_check_for_update_ignores_network_errors():
    from updates import check_for_update

    def offline(*_args, **_kwargs):
        raise OSError("offline")

    assert check_for_update(opener=offline) is None
