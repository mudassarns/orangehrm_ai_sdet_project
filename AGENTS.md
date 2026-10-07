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

The Playwright MCP server is configured with external secrets.

For OrangeHRM credentials, use these configured secret names through the Playwright MCP input tools:

- `ORANGEHRM_USERNAME`
- `ORANGEHRM_PASSWORD`

For credential entry, use the Playwright MCP **Type text** tool (`browser_type`) directly so that the MCP secret-resolution mechanism resolves the configured values.

Do not type `<secret>...</secret>` literally.

Do not expose resolved secret values in responses.

Do not inspect, read, search, unpack, or expose:

`D:\Automation\automation-secrets\.mcp-secrets`

Do not search the filesystem or environment for the credential values.

## Project integrity

Do not create, modify, or delete files unless the task requires it.

Keep generated automation independent from any other OrangeHRM automation implementation.

Do not copy existing automation implementations into this project.
