---
name: playwright-installer-intellij-junie
description: A skill to guide the installation and configuration of Playwright testing within IntelliJ IDEA alongside the Junie AI assistant.
---

# IntelliJ IDEA with Junie Installation

This skill provides the steps to set up AI-assisted Playwright testing inside JetBrains IntelliJ IDEA using the Junie plugin.

## Prerequisites
- Node.js installed.
- IntelliJ IDEA (Ultimate or Community) installed.
- Junie plugin installed from the JetBrains marketplace.

## Installation Steps
1. **Initialize Playwright**
   Open the terminal inside IntelliJ and run `npm init playwright@latest`.
   Select TypeScript for maximum compatibility.
2. **Configure Junie**
   - Open IntelliJ Settings > Plugins > Installed, confirm Junie is active.
   - Authorize Junie according to the plugin's onboarding instructions.
3. **Index Documentation**
   Provide the `Playwright-skill` repository files, including these markdown skills, to the Junie context. Junie will read these patterns to enforce best practices when writing new tests or diagnosing failures.
