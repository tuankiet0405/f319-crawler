---
description: Challenge and improve BDD spec before implementation
---

Skills required: adversarial-reviewer

Challenge a BDD spec (from `/bdd-spec`) before proceeding to `/bdd-dev`. Catches missing scenarios, user flow gaps, and product impact blindspots.

## Inputs

- A BDD spec file in `docs/specs/*.md` (produced by `/bdd-spec`)

## Workflow

1. **Read the spec** — understand the feature, user stories, and all scenarios
2. **Check existing product context** — identify which current features, shared components, or APIs are affected by this change
3. **Apply adversarial-reviewer skill** — use both the general and BDD-specific attack vectors defined in the skill
4. **Record challenges in Antigravity artifacts** — do NOT write challenge notes into the spec file. Use the challenge format from the skill.
5. **Debate with user** — present challenges, get the author's defense, reach verdicts
6. **Produce verdict report** in Antigravity artifacts
7. **Update spec** — only after challenges are resolved. The spec is the finalized document.

## Rules

- The spec file (`docs/specs/*.md`) contains only finalized, debate-won content
- All challenge rounds, debate logs, and verdict reports stay in Antigravity's artifacts
- If the verdict is REVISE, update the spec and re-run the review
- If the verdict is ACCEPTED, proceed to `/bdd-dev`

## Next step

After spec passes review → run `/bdd-dev` to implement

