from pathlib import Path

from pytest_mock import MockerFixture

from ragdemo.auth import capture_session


def test_capture_session_opens_visible_browser_and_saves_state(
    tmp_path: Path,
    mocker: MockerFixture,
) -> None:
    storage_state_path = tmp_path / "secrets/storage_state.json"
    playwright = mocker.MagicMock()
    manager = mocker.MagicMock()
    manager.__enter__.return_value = playwright
    mocker.patch("ragdemo.auth.sync_playwright", return_value=manager)
    wait_for_user = mocker.Mock()

    capture_session(
        base_url="https://wiki.example.internal",
        storage_state_path=storage_state_path,
        wait_for_user=wait_for_user,
    )

    playwright.chromium.launch.assert_called_once_with(headless=False)
    page = playwright.chromium.launch.return_value.new_context.return_value.new_page.return_value
    page.goto.assert_called_once_with(
        "https://wiki.example.internal",
        wait_until="domcontentloaded",
    )
    wait_for_user.assert_called_once()
    context = playwright.chromium.launch.return_value.new_context.return_value
    context.storage_state.assert_called_once_with(path=storage_state_path)
