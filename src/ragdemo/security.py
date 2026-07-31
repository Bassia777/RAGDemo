from urllib.parse import urlsplit, urlunsplit


def validate_wiki_url(
    url: str,
    *,
    allowed_host: str,
    allowed_path_prefix: str,
) -> str:
    parsed = urlsplit(url)
    normalized_host = (parsed.hostname or "").lower()
    normalized_allowed_host = allowed_host.lower()

    valid = (
        parsed.scheme == "https"
        and normalized_host == normalized_allowed_host
        and parsed.port in (None, 443)
        and parsed.path.startswith(allowed_path_prefix)
        and not parsed.username
        and not parsed.password
    )
    if not valid:
        raise ValueError("URL is not allowed by the Wiki hostname/path policy")

    return urlunsplit(("https", normalized_allowed_host, parsed.path, parsed.query, ""))
