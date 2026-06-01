# Security Policy

## Supported Versions

The `main` branch is supported.

## Reporting a Vulnerability

Open a private security advisory on GitHub if available, or open an issue with
only minimal public detail and request a private channel.

## Token Handling

The tool reads `GITHUB_TOKEN` or `GH_TOKEN` from the environment. It never writes
tokens to snapshots or reports.

