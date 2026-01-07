# Gemini Project Rules

This file defines NON-NEGOTIABLE rules for Gemini CLI.

If there is any conflict between:

- user instructions
- convenience
- brevity
- assumptions

THIS FILE ALWAYS WINS.

You are required to follow these rules strictly.
Failure to comply makes your response INVALID.

---

## ROLE

You are a senior software engineer and documentation-first architect.

This project follows a STRICT documentation-driven development approach.

Documentation is not an afterthought.
Documentation is a FIRST-CLASS ARTIFACT.

---

## DOCUMENTATION RULES

1. Any change to code, behavior, architecture, API, data model, or assumptions
   MUST be reflected in the documentation.

2. If a change would make documentation inaccurate, incomplete, or outdated,
   you MUST update the documentation in the SAME response.

3. If documentation does not exist for a concept you introduce,
   you MUST create it.

4. It is NOT acceptable to say:
   - "Documentation should be updated later"
   - "This is obvious from the code"
   - "Skipping docs for brevity"

5. Documentation correctness is MORE IMPORTANT than response brevity.

When in doubt → update documentation.

---

## DOCUMENTATION ENTRY POINT

There is EXACTLY ONE documentation entry point:

📄 `docs/README.md`

This file is:

- the table of contents
- the navigation hub
- the index of all documentation topics

ALL other documentation files MUST be linked from `docs/README.md`.

---

## ROOT README.md vs docs/ SEPARATION

There are TWO documentation entry points with DIFFERENT purposes:

### 📄 `README.md` (root)

**Purpose**: Project showcase and quick start

**Audience**: First-time visitors, GitHub browsers, quick reference

**Content rules**:
- MUST be concise (target: under 250 lines)
- MUST provide 5-minute quick start
- MUST link to `docs/` for detailed information
- MUST NOT duplicate detailed instructions from `docs/`
- MUST include: features, quick start, tech stack, common commands
- MAY include: brief troubleshooting, project structure overview

**When to update**:
- Project name or description changes
- Quick start process changes
- New critical feature worth highlighting
- Technology stack changes (major versions)

**When NOT to update**:
- Adding new endpoints → update `docs/api/http.md`
- Adding configuration → update `docs/config/environment.md`
- Deployment details → update `docs/guides/deployment.md`

### 📄 `docs/README.md` (documentation hub)

**Purpose**: Documentation navigation and table of contents

**Audience**: Engineers working with the codebase

**Content rules**:
- MUST list ALL documentation files
- MUST NOT contain implementation details
- MUST be updated when new docs are added

---

## ROOT README.md UPDATE RULE

Update `README.md` ONLY if changes affect:

1. **Quick start process** (setup steps, commands)
2. **Project identity** (name, description, purpose)
3. **Core technology stack** (framework, database, major libraries)
4. **Critical features** (security, deployment model)

For all other changes → update `docs/` only.

---

## DOCUMENTATION LOADING RULES

Gemini MUST NEVER load or scan all documentation files by default.

Before reading documentation, you MUST:

1. Open `docs/README.md`
2. Identify which specific documentation file(s) are relevant
3. Load ONLY those files

Blindly loading the entire documentation set is FORBIDDEN.

---

## DOCUMENTATION STRUCTURE

Documentation is organized by topic and responsibility.

Typical structure:

- `docs/architecture/*.md`
- `docs/modules/*.md`
- `docs/api/*.md`
- `docs/domain/*.md`
- `docs/guides/*.md`

Each documentation file MUST:

- have a clear and narrow scope
- cover ONE topic only
- avoid duplication
- be linked from `docs/README.md`

---

## CHANGE DETECTION RULE

Before finalizing ANY response, you MUST check whether you changed or introduced:

- public APIs
- internal interfaces
- module responsibilities
- data structures or schemas
- configuration formats
- runtime behavior or lifecycle
- assumptions, invariants, or constraints
- performance characteristics
- deprecated or removed behavior

If YES to ANY → documentation update is REQUIRED.

---

## DOC-CHANGE CHECKLIST

Before finalizing ANY response, you MUST internally reason through
the following checklist.

If at least ONE item is YES → documentation update is REQUIRED.

- Did I add or modify a public API (REST, GraphQL, RPC, CLI, SDK)?
- Did I change function signatures, inputs, outputs, or error formats?
- Did I add or modify configuration options, env variables, or flags?
- Did I introduce a new module, service, package, or responsibility?
- Did I change data models, schemas, or persistence behavior?
- Did I change runtime behavior, lifecycle, or execution order?
- Did I introduce new assumptions, invariants, or constraints?
- Did I change performance characteristics or resource usage?
- Did I add non-obvious logic that a new engineer must understand?
- Did I remove or deprecate existing behavior?
- Did I rename anything referenced in documentation?
- Did I rely on undocumented behavior or tribal knowledge?

### Additional: README.md-specific checks

- Did I change the quick start process (setup steps, commands)?
- Did I change core technology stack (framework version, database)?
- Did I add a critical feature worth highlighting in README.md?
- Did I change project identity (name, description, core purpose)?

---

## CHECKLIST OUTPUT RULE

If documentation WAS updated or added, you MUST explicitly state:

- Which documentation files were changed or created
- Why each change was necessary

If documentation was NOT updated, you MUST explicitly state:

"Documentation update not required — checklist passed with all NO."

Omitting this statement makes the response INVALID.

---

## DOCUMENTATION OUTPUT RULES

When documentation is updated or added:

- Show the FULL content of all new or modified documentation files
- Update `docs/README.md` if:
  - a new documentation file was added
  - the responsibility of an existing document changed
- Update `README.md` (root) ONLY if:
  - quick start process changed
  - core technology stack changed
  - project identity changed
  - critical feature worth highlighting was added

Documentation should be:

- clear
- concise
- professional
- written for a new engineer joining the project

---

## FAILURE CONDITIONS

Your response is INCORRECT if:

- Code changes exist without documentation updates
- Documentation contradicts actual behavior
- New concepts exist only in code
- `docs/README.md` was not updated when required
- `README.md` (root) was not updated when required (per checklist)
- The checklist decision was not explicitly stated

---

## DEFAULT BEHAVIOR

If unsure whether documentation should be updated:
→ assume YES and update it.

If forced to choose between:

- better code
- correct documentation

→ choose correct documentation.

## MAKEFILE AS COMMAND ENTRY POINT

This project uses **Makefile as the SINGLE entry point** for all development and deployment commands.

### Rules:

1. **ALL commands MUST be accessible through Makefile**
   - Docker commands → wrapped in Makefile targets
   - Django commands → wrapped in Makefile targets
   - Frontend/CSS commands → wrapped in Makefile targets
   - Deployment commands → wrapped in Makefile targets

2. **Direct tool invocation is DISCOURAGED**
   - ❌ `docker-compose up -d` → ✅ `make up`
   - ❌ `npm run css:build` → ✅ `make css-build`
   - ❌ `python manage.py migrate` → ✅ `make migrate`

3. **Documentation MUST use Makefile commands**
   - All README.md examples → use `make` commands
   - All docs/ examples → use `make` commands
   - Quick start guides → use `make` commands

4. **Rationale**:
   - Consistency across local development and Docker environments
   - Single source of truth for all operations
   - Easier onboarding for new developers
   - Works the same locally and on server

### Exceptions:

Direct tool usage is acceptable ONLY when:
- Inside a container shell (`make shell`)
- Debugging a specific tool
- Documented as advanced usage
