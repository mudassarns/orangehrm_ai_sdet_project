# AI/MCP Project Instructions

## Project

This is a standalone AI-assisted SDET project for testing OrangeHRM using Playwright MCP.

Current project path:

`D:\Automation\orangehrm_ai_sdet_project`

## Requirements

The current feature requirements document is:

`D:\Automation\Requirements\Login_QA_Requirements_MCP.docx`

This document covers the login feature and its acceptance criteria only.

Additional features may use separate requirements documents. Do not assume that this document contains requirements for the entire project.

## Playwright MCP

Use the configured Microsoft Playwright MCP server for browser investigation and interaction.

Use Playwright MCP browser tools directly.

For text entry, use the Playwright MCP **Type text** tool (`browser_type`) directly.

Do not use `browser_run_code_unsafe` for browser interaction or credential entry.

## Credential handling

### Playwright MCP credentials

The Playwright MCP server is configured with external secrets.

For OrangeHRM browser exploration, use these configured secret names through the Playwright MCP input tools:

- `ORANGEHRM_USERNAME`
- `ORANGEHRM_PASSWORD`

For credential entry, use the Playwright MCP **Type text** tool (`browser_type`) directly so the MCP secret-resolution mechanism resolves the configured values.

Do not type `<secret>...</secret>` literally as ordinary browser input.

Never expose resolved credential values in responses, logs, screenshots, reports, or generated files.

Do not inspect, read, search, unpack, or expose:

`D:\Automation\automation-secrets\.mcp-secrets`

Do not search the filesystem or environment for credential values.

### Python pytest credentials

The Python pytest tests use the existing `credentials` fixture, which reads `ORANGEHRM_USERNAME` and `ORANGEHRM_PASSWORD` from the Python process environment.

For local VS Code test execution and debugging:

- Store the two variables in the project-root `.env` file.
- The project-root `conftest.py` calls `load_dotenv()` to load variables from the project-root `.env` file for pytest execution.
- The `.vscode/settings.json` file enables pytest in VS Code and configures test discovery under `tests`. Keep this configuration for consistent VS Code Test Explorer and test-debugging support in this project.
- The project-root `.gitignore` must exclude `.env`. Never stage, commit, or share this file.
- Never print, display, or disclose the credential values. Do not open or inspect `.env` to retrieve the values.

The Playwright MCP secret-resolution mechanism and the Python pytest environment are separate mechanisms. MCP secrets do not automatically become Python environment variables, and instructions in this document do not inject credentials into either process.

If a pytest test is skipped because `ORANGEHRM_USERNAME` or `ORANGEHRM_PASSWORD` is unavailable, report the missing environment configuration without exposing credentials. Do not modify authentication code or create another credential-loading mechanism without explicit approval.

## Project integrity

Do not create, modify, or delete files unless the task requires it.

Keep generated automation independent from any other OrangeHRM automation implementation.

Do not copy existing automation implementations into this project.
