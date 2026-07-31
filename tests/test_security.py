import pytest

from ragdemo.security import validate_wiki_url


def test_accepts_https_url_inside_allowed_path() -> None:
    result = validate_wiki_url(
        "https://wiki.example.internal/spaces/learning/page-1",
        allowed_host="wiki.example.internal",
        allowed_path_prefix="/spaces/learning/",
    )
    assert result == "https://wiki.example.internal/spaces/learning/page-1"


def test_accepts_configured_http_url_with_nondefault_port() -> None:
    result = validate_wiki_url(
        "http://wiki.bigo.sg:8090/pages/viewpage.action?pageId=635831163",
        allowed_host="wiki.bigo.sg",
        allowed_path_prefix="/pages/",
        allowed_scheme="http",
        allowed_port=8090,
    )

    assert result == "http://wiki.bigo.sg:8090/pages/viewpage.action?pageId=635831163"


@pytest.mark.parametrize(
    "url",
    [
        "http://wiki.example.internal/spaces/learning/page-1",
        "https://evil.example/spaces/learning/page-1",
        "https://wiki.example.internal/admin/page-1",
        "https://wiki.example.internal.evil.example/spaces/learning/page-1",
        "javascript:alert(1)",
    ],
)
def test_rejects_url_outside_allowlist(url: str) -> None:
    with pytest.raises(ValueError, match="URL is not allowed"):
        validate_wiki_url(
            url,
            allowed_host="wiki.example.internal",
            allowed_path_prefix="/spaces/learning/",
        )
