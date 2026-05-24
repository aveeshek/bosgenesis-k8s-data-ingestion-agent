# Codex Config Specification

## Role

This directory will describe Codex-local configuration for working with the project.

## Responsibilities

- Define expected local paths and non-secret defaults.
- Document how local Codex tasks should start tests, formatters, and validation.
- Keep machine-specific values out of committed runtime code.

## Constraints

- Do not store credentials.
- Do not store Kubernetes tokens.
- Do not store production endpoints unless already public and non-sensitive.

