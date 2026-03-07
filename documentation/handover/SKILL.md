---
name: playwright-handover
description: A skill to perform a structured handover to a human-in-the-loop after completing a task.
---

# Handover to Human-in-the-Loop

This skill ensures that every task completion is followed by a comprehensive handover document that summarizes the changes, patterns used, and identifies potential areas for improvement or new skill creation.

## 1. Storage & Naming

- **Directory**: `<test_documentation_root>/handovers/`
  - Default root: `docs/tests/`
- **Filename Format**: `YYYYMMDD_HHmm_PlaywrightSkillsHAndover.md` 
  - *Note: On Windows, colons are not allowed in filenames, so use `HHmm` or `HH_mm`.*

## 2. Content Structure

The handover document must be written in markdown and include the following sections:

### What was done
A clear summary of the actions taken during the task.

### Skills and Subskills used
A list of all skills and subskills utilized, with a brief explanation of *why* they were used.

### Non-skill actions & Suggestions
List any actions performed that were not covered by an existing skill. Suggest new skills or subskills for these actions and outline how they should be implemented.

### Patterns used
Which architectural or implementation patterns were used (e.g., POM, Fixtures, etc.) and the rationale behind choosing them.

### Anti-patterns used
Identify any anti-patterns that were unavoidable and explain why there was no other way to do it.

### Strengths of the changes
What are the key benefits of the changes made?

### Weaknesses of the changes
What are the potential risks or limitations of the changes?

### How things could be improved
Concrete suggestions on how the implementation or the process could be improved in the future.

### Files added/modified
List all files added or modified, categorized into:
- **Documentation**
- **POMs**
- **Test Scripts**
- **Configurations**
- **Other**
Include a brief "why" for each category.

## 3. Execution

This handover document should be made and stored at the end of every task unless the user asks otherwise.
