---
description: Document changelogs and user manual after done implementation
---

Skills required: docs-writing

After finishing implementation and get approval from user, document the following:

0. **Check E2E screenshots first** — look in `tests/output/screenshots/docs/` before manually capturing. See the `e2e-test-writer` skill for the full screenshot pattern.

1. Classify the implementation into two types: **feature** or **technical**:
   - **Feature**: write/update user manual in `docs/user_manual/docs/*.md`. Prefer E2E screenshots (see `docs-writing` skill Step 1). Ensure `docs/user_manual/` always reflects the latest features.
   - **Technical** (e.g., technical changes, architecture, design patterns): write/update developer manual in `docs/developer_manual/`.

2. Write journal file into `docs/changelogs` folder with this format: `<yyyymmdd>_<short_summary>.md`. Content of journal file:
- Short summary of what changes, focus on important changes
- How the changes are implemented
- Discussion logs between user and agent

To gather context for journal:
- Get directly from working session with user, this is the major content you used to write short_summary in file name
- Use `git diff` to get changes