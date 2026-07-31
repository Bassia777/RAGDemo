from urllib.parse import urlsplit, urlunsplit


def validate_wiki_url(
    url: str,
    *,
    allowed_host: str,
    allowed_path_prefix: str,
    allowed_scheme: str = "https",
    allowed_port: int | None = None,
) -> str:
    parsed = urlsplit(url)
    normalized_host = (parsed.hostname or "").lower()
    normalized_allowed_host = allowed_host.lower()

    default_ports = {"http": 80, "https": 443}
    expected_port = allowed_port or default_ports.get(allowed_scheme)
    actual_port = parsed.port or default_ports.get(parsed.scheme)

    valid = (
        parsed.scheme == allowed_scheme
        and normalized_host == normalized_allowed_host
        and actual_port == expected_port
        and parsed.path.startswith(allowed_path_prefix)
        and not parsed.username
        and not parsed.password
    )
    if not valid:
        raise ValueError("URL is not allowed by the Wiki hostname/path policy")

    default_port = default_ports.get(allowed_scheme)
    netloc = normalized_allowed_host
    if expected_port is not None and expected_port != default_port:
        netloc = f"{netloc}:{expected_port}"

    return urlunsplit((allowed_scheme, netloc, parsed.path, parsed.query, ""))
