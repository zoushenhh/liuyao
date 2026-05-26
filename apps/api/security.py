import ipaddress
import re
import time
from urllib.parse import urlparse

_interpret_timestamps: list[float] = []

# RFC 6890 / RFC 1918 private + loopback + link-local blocks
_PRIVATE_NETS = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
]


def validate_base_url(url: str) -> str:
    url = url.strip()
    if not url:
        return url
    if not (url.startswith("http://") or url.startswith("https://")):
        msg = "Base URL 必须以 http:// 或 https:// 开头"
        raise ValueError(msg)
    parsed = urlparse(url)
    host = parsed.hostname
    if host:
        try:
            addr = ipaddress.ip_address(host)
        except ValueError:
            # Hostname — resolve and check (best effort)
            try:
                import socket
                addr = ipaddress.ip_address(socket.gethostbyname(host))
            except (OSError, ValueError):
                return url
        for net in _PRIVATE_NETS:
            if addr in net:
                msg = "不允许访问内网地址"
                raise ValueError(msg)
    return url


def redact_api_key(key: str) -> str:
    if not key or len(key) < 8:
        return "*" * min(len(key) or 1, 4)
    return key[:4] + "*" * (len(key) - 8) + key[-4:]


def check_rate_limit(max_per_minute: int = 10) -> bool:
    now = time.time()
    cutoff = now - 60
    global _interpret_timestamps
    _interpret_timestamps = [t for t in _interpret_timestamps if t > cutoff]
    if len(_interpret_timestamps) >= max_per_minute:
        return False
    _interpret_timestamps.append(now)
    return True
