# Langflow Visualizations

This folder contains visualization-only Langflow artifacts for the BOS Genesis K8s Data Ingestion Agent.

The graph is intended to show architecture and data flow only. It does not execute scans, call MCP tools, connect to sinks, or require credentials.

## Files

- `data-ingestion-agent-architecture.json` - importable visual graph showing the agent flow from Codex/GPT/agents through the data-ingestion-agent MCP endpoint, internal workflow, existing MCP tools, storage sinks, and observability.

## Usage

Import the JSON into Langflow as a reference diagram. Treat every node as a documentation node, not a runtime component.
