from collections.abc import Callable
from pathlib import Path

from playwright.sync_api import sync_playwright


def capture_session(
    *,
    base_url: str,
    storage_state_path: Path,
    wait_for_user: Callable[[str], str | None] = input,
) -> None:
    storage_state_path.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto(base_url, wait_until="domcontentloaded")
        wait_for_user("请在浏览器完成 SSO 登录，确认已进入 Wiki 后按 Enter 保存会话：")
        context.storage_state(path=storage_state_path)
        browser.close()
