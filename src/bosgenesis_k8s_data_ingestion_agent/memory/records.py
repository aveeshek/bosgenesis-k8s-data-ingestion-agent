"""Memory record contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4


class MemoryType(StrEnum):
    SESSION = "session"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"


@dataclass(frozen=True)
class MemoryRecord:
    memory_id: UUID = field(default_factory=uuid4)
    memory_type: MemoryType = MemoryType.SEMANTIC
    text: str = ""
    namespace: str = "bosgenesis"
    source: str = ""
    entity_type: str = ""
    entity_name: str = ""
    entity_key: str = ""
    run_id: UUID | None = None
    correlation_id: str | None = None
    content_hash: str | None = None
    observed_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

