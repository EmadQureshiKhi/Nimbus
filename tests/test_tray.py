"""Unit tests for tray.py — system tray menu + folder actions.

Tray icon construction needs a QApplication. We use a session-scoped
fixture that creates one if none exists. The actual rendering
(``self._icon.show()``) is silently no-op'd on systems without a
display, so tests run headless cleanly.
"""
from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def qapp():
    """Session-shared QApplication. Created once; reused across tests."""
    from PyQt6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


def test_tray_module_importable():
    import tray  # noqa: F401


class TestNimbusTrayMenu:
    """The tray menu exposes settings, folders, session export, and quit."""

    @pytest.fixture(autouse=True)
    def _suppress_real_onboarding_persistence(self, mocker):
        """Tray construction must never write the developer's real keyring."""
        mocker.patch("tray.config.onboarding_seen", return_value=True)

    def test_menu_has_five_actions_in_order(self, qapp, mocker):
        """The 5 visible menu items + 1 separator. Verified by reading
        QMenu.actions() in order."""
        from tray import NimbusTray
        on_quit = mocker.MagicMock()
        on_settings = mocker.MagicMock()
        on_export = mocker.MagicMock()
        t = NimbusTray(
            on_quit=on_quit,
            on_settings=on_settings,
            on_export_session_history=on_export,
        )

        actions = [a for a in t._menu.actions() if not a.isSeparator()]
        labels = [a.text() for a in actions]
        assert labels == [
            "Settings...",
            "Pause push-to-talk",
            "Open Knowledge Folder",
            "Open Memory Folder",
            "Export Session History",
            "Quit Nimbus",
        ]

    def test_export_action_triggers_export_callback(self, qapp, mocker):
        from tray import NimbusTray
        on_export = mocker.MagicMock()
        t = NimbusTray(
            on_quit=mocker.MagicMock(),
            on_settings=mocker.MagicMock(),
            on_export_session_history=on_export,
        )

        action = next(
            a for a in t._menu.actions() if a.text() == "Export Session History"
        )
        action.trigger()
        on_export.assert_called_once()

    def test_pause_action_is_checkable_and_notifies_app(self, qapp, mocker):
        from tray import NimbusTray
        changed = mocker.MagicMock()
        tray = NimbusTray(
            on_quit=mocker.MagicMock(), on_settings=mocker.MagicMock(),
            on_pause_changed=changed,
        )
        action = next(a for a in tray._menu.actions() if a.text() == "Pause push-to-talk")
        assert action.isCheckable()
        action.trigger()
        changed.assert_called_once_with(True)

    def test_first_launch_shows_configured_hotkey_onboarding_once(self, qapp, mocker):
        """The balloon uses config.HOTKEY and only marks state after display."""
        mocker.patch("tray.config.onboarding_seen", return_value=False)
        marked = mocker.patch("tray.config.mark_onboarding_seen")
        mocker.patch("tray.config.HOTKEY", "ctrl+shift+f2")
        show_message = mocker.patch("tray.QSystemTrayIcon.showMessage")

        from tray import NimbusTray
        NimbusTray(on_quit=mocker.MagicMock(), on_settings=mocker.MagicMock())

        show_message.assert_called_once()
        assert "Ctrl+Shift+F2" in show_message.call_args.args[1]
        assert "Right-click" in show_message.call_args.args[1]
        marked.assert_called_once()

    def test_seen_onboarding_never_shows_again(self, qapp, mocker):
        mocker.patch("tray.config.onboarding_seen", return_value=True)
        marked = mocker.patch("tray.config.mark_onboarding_seen")
        show_message = mocker.patch("tray.QSystemTrayIcon.showMessage")

        from tray import NimbusTray
        NimbusTray(on_quit=mocker.MagicMock(), on_settings=mocker.MagicMock())

        show_message.assert_not_called()
        marked.assert_not_called()

    def test_quit_action_triggers_on_quit_callback(self, qapp, mocker):
        from tray import NimbusTray
        on_quit = mocker.MagicMock()
        on_settings = mocker.MagicMock()
        t = NimbusTray(on_quit=on_quit, on_settings=on_settings)

        quit_action = next(
            a for a in t._menu.actions() if a.text() == "Quit Nimbus"
        )
        quit_action.trigger()
        on_quit.assert_called_once()
        on_settings.assert_not_called()

    def test_settings_action_triggers_on_settings_callback(self, qapp, mocker):
        from tray import NimbusTray
        on_quit = mocker.MagicMock()
        on_settings = mocker.MagicMock()
        t = NimbusTray(on_quit=on_quit, on_settings=on_settings)

        settings_action = next(
            a for a in t._menu.actions() if a.text() == "Settings..."
        )
        settings_action.trigger()
        on_settings.assert_called_once()
        on_quit.assert_not_called()

    def test_open_kb_folder_uses_kb_dir_and_creates_if_missing(
        self, qapp, mocker, tmp_path: Path
    ):
        """Open Knowledge Folder must call os.startfile on KB_DIR
        AND mkdir-p the path if it doesn't exist. First-launch users
        haven't dropped any .md files yet — no error dialog."""
        kb_path = tmp_path / "knowledge"
        assert not kb_path.exists()

        mocker.patch("tray.KB_DIR", kb_path)
        startfile_mock = mocker.patch("tray.os.startfile")

        from tray import NimbusTray
        t = NimbusTray(on_quit=mocker.MagicMock(), on_settings=mocker.MagicMock())
        action = next(
            a for a in t._menu.actions()
            if a.text() == "Open Knowledge Folder"
        )
        action.trigger()

        assert kb_path.exists(), "Expected KB folder to be auto-created"
        startfile_mock.assert_called_once_with(str(kb_path))

    def test_open_memory_folder_uses_memory_dir_and_creates_if_missing(
        self, qapp, mocker, tmp_path: Path
    ):
        mem_path = tmp_path / "memory"
        mocker.patch("tray.MEMORY_DIR", mem_path)
        startfile_mock = mocker.patch("tray.os.startfile")

        from tray import NimbusTray
        t = NimbusTray(on_quit=mocker.MagicMock(), on_settings=mocker.MagicMock())
        action = next(
            a for a in t._menu.actions()
            if a.text() == "Open Memory Folder"
        )
        action.trigger()

        assert mem_path.exists()
        startfile_mock.assert_called_once_with(str(mem_path))

    def test_raises_runtime_error_when_system_tray_unavailable(
        self, qapp, mocker
    ):
        """If QSystemTrayIcon.isSystemTrayAvailable() returns False (rare
        Windows config — kiosk mode, custom shell, certain VMs), the
        constructor must raise RuntimeError so the caller can show a
        QMessageBox + exit cleanly. Without this guard the tray icon
        silently doesn't appear and users have no diagnostic."""
        from tray import NimbusTray
        mocker.patch(
            "tray.QSystemTrayIcon.isSystemTrayAvailable",
            return_value=False,
        )
        with pytest.raises(RuntimeError, match="System tray is not available"):
            NimbusTray(
                on_quit=mocker.MagicMock(),
                on_settings=mocker.MagicMock(),
            )
