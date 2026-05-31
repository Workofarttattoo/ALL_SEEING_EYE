"""Target parsing and resolution utilities."""

from __future__ import annotations

import socket
from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass
class Target:
    raw: str
    domain: str
    scheme: str
    ip: str | None = None

    @classmethod
    def from_input(cls, value: str) -> "Target":
        normalized = value if "://" in value else f"http://{value}"
        parsed = urlparse(normalized)
        domain = parsed.netloc or parsed.path.split("/")[0]
        if ":" in domain:
            domain = domain.split(":")[0]
        return cls(raw=value, domain=domain, scheme=parsed.scheme or "http")

    def resolve(self) -> str:
        if self.ip:
            return self.ip
        self.ip = socket.gethostbyname(self.domain)
        return self.ip

    def url(self, path: str = "", use_https: bool = False) -> str:
        scheme = "https" if use_https else self.scheme
        if not path.startswith("/"):
            path = f"/{path}" if path else ""
        return f"{scheme}://{self.domain}{path}"
