#!/usr/bin/env python3
"""Initialize Redis keyspace without requiring redis-cli or third-party packages."""

from __future__ import annotations

import os
import socket
from typing import Iterable


def encode_command(parts: Iterable[str]) -> bytes:
    encoded = []
    items = [str(part).encode("utf-8") for part in parts]
    encoded.append(f"*{len(items)}\r\n".encode("ascii"))
    for item in items:
        encoded.append(f"${len(item)}\r\n".encode("ascii"))
        encoded.append(item + b"\r\n")
    return b"".join(encoded)


def read_response(sock: socket.socket):
    prefix = sock.recv(1)
    if not prefix:
        raise RuntimeError("Redis closed the connection")

    line = b""
    while not line.endswith(b"\r\n"):
        chunk = sock.recv(1)
        if not chunk:
            raise RuntimeError("Redis closed the connection while reading response")
        line += chunk

    payload = line[:-2].decode("utf-8", errors="replace")
    marker = prefix.decode("ascii")

    if marker == "+":
        return payload
    if marker == "-":
        raise RuntimeError(payload)
    if marker == ":":
        return int(payload)
    if marker == "$":
        size = int(payload)
        if size == -1:
            return None
        data = b""
        while len(data) < size + 2:
            data += sock.recv(size + 2 - len(data))
        return data[:-2].decode("utf-8", errors="replace")
    if marker == "*":
        count = int(payload)
        return [read_response(sock) for _ in range(count)]

    raise RuntimeError(f"Unsupported Redis response marker: {marker}")


def call(sock: socket.socket, *parts: str):
    sock.sendall(encode_command(parts))
    return read_response(sock)


def ignore_busygroup(error: RuntimeError) -> None:
    if "BUSYGROUP" not in str(error):
        raise error


def main() -> None:
    host = os.environ.get("REDIS_HOST", "redis-master.bosgenesis.svc.cluster.local")
    port = int(os.environ.get("REDIS_PORT", "6379"))
    db = os.environ.get("REDIS_DB", "0")
    password = os.environ.get("REDIS_PASSWORD", "")
    prefix = os.environ.get("REDIS_KEY_PREFIX", "bg:k8s-ingestion")
    group = os.environ.get("REDIS_CONSUMER_GROUP", "k8s-ingestion-agent")
    initialized_at = os.environ.get("INITIALIZED_AT", "")

    with socket.create_connection((host, port), timeout=10) as sock:
        if password:
            call(sock, "AUTH", password)
        call(sock, "SELECT", db)
        call(
            sock,
            "HSET",
            f"{prefix}:meta",
            "agent",
            "bosgenesis-k8s-data-ingestion-agent",
            "namespace",
            "bosgenesis",
            "owner",
            "bosgenesis",
            "initialized_at",
            initialized_at,
        )

        for stream in ("changes", "sink-audit"):
            try:
                call(sock, "XGROUP", "CREATE", f"{prefix}:stream:{stream}", group, "$", "MKSTREAM")
            except RuntimeError as error:
                ignore_busygroup(error)


if __name__ == "__main__":
    main()
