"""Thin agentic memory abstraction."""

from bosgenesis_k8s_data_ingestion_agent.memory.records import MemoryRecord, MemoryType
from bosgenesis_k8s_data_ingestion_agent.memory.record_builder import MemoryRecordBuilder
from bosgenesis_k8s_data_ingestion_agent.memory.router import MemoryRouter

__all__ = ["MemoryRecord", "MemoryRecordBuilder", "MemoryRouter", "MemoryType"]

