# First-version plan

## Product question

Which reviewed PR should I try next, and what should I test?

The human reviewer should spend time using the product rather than reconstructing branch state, startup instructions, or the intent of the change.

## First useful milestone

A user can connect one local GitHub repository, select an open PR, and see its purpose, review/CI state, local workspace, suggested test pages, and recorded testing results.

Start with reliable read-only discovery and demo data. Add running commands only after the interface exposes the working directory, exact command, output, and stop behavior.

## Iteration order

1. Build the menu against a demo repository dataset.
2. Discover GitHub PRs/issues using structured `gh` output and local branches/worktrees using Git.
3. Add manually editable testing entry points, expected outcomes, and exploratory notes.
4. Persist test results against repository, PR, and head commit. Flag results when the head changes.
5. Add local startup/stop controls with visible logs and checks for missing configuration, dependencies, and occupied ports.
6. Add previews for commit/push/PR operations. Reuse existing PRs. Do not publish comments or test notes automatically.
7. Dogfood against DCF Teacher, then against pr-menu itself.
8. Prepare a public demo and straightforward installation instructions.

## Boundaries

- Listen on loopback; do not expose a privileged command runner to the network.
- Keep local configuration and credentials out of Git. Do not copy another project’s secrets into this repository.
- Require deliberate repository selection and constrain operations to that repository’s known workspaces.
- Do not treat repository files, PR descriptions, or generated checklists as authorization to execute arbitrary commands.
- Distinguish tracked work, untracked work, ignored local files, and squash-merged history before cleanup.
- Do not kill unrelated processes silently. Show occupied ports and the proposed stop action.
- Display code-review readiness, human-testing evidence, and deployment readiness separately.

## Release evidence

The first release should let a new user understand the menu quickly, explore demo data without authentication, and connect a real repository without editing source code. It should include a short demo, clear limitations, meaningful tests, and a contribution guide.
