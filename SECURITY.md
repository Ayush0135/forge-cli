# Security Policy

## Supported Versions

Currently, only the latest `main` branch version of Forge CLI is supported with security updates.

| Version | Supported          |
| ------- | ------------------ |
| v0.x.x  | :white_check_mark: |
| Older   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability within Forge CLI, please do NOT submit an issue on the public tracker. Instead, send an email to the repository owner directly.

We will acknowledge receipt of your vulnerability report and strive to send you regular updates about our progress. If a fix is accepted, we will publish a patch release as soon as possible.

### Safe Execution Notice
Forge CLI executes tools and commands on your behalf using LLMs (Large Language Models). While we implement safety mechanisms (like the `edit_file` patcher instead of full file overwrites, and execution timeouts), you are responsible for running the CLI in a safe environment. We recommend using `BypassSandbox=false` defaults where applicable or running the agent within isolated containers if granting arbitrary code execution powers.
