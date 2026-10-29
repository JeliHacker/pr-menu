# pr-menu

A pull request menu for people who build faster than they can test.

Code-reviewed PRs pile up. Human attention becomes the bottleneck. pr-menu helps you pick the next change to try, run it locally, and record whether it actually works and feels intuitive.

The goal is to help you become your own most passionate user: dogfood real workflows, notice friction, and turn that experience into better software.

## The workflow

1. Connect a local GitHub repository.
2. Browse a menu of PRs with their purpose, code-review state, and automated checks.
3. Choose a PR and see what changed, where to go, and what to try.
4. Start its local environment in an appropriate workspace.
5. Use the feature, including the paths a checklist did not anticipate.
6. Record what worked, what felt awkward, and what broke.
7. Return to GitHub with evidence for the merge decision or a useful follow-up.

Testing results belong to the exact commit that was tried. New commits make prior results potentially stale; they do not silently inherit a pass.

## First version

The initial implementation will be a local application with a browser interface and a backend bound to loopback. GitHub authentication will use an existing `gh` login. Git is the initial version-control interface; contributors do not need Jujutsu.

The first repository we will dogfood against is DCF Teacher. Repository paths, test URLs, startup commands, and results must be configurable rather than hardcoded to its environment.

The core experience is a human-testing queue. Issue listings and branch/workspace status support that experience. The project is not intended to become a general-purpose issue tracker or an automated approval engine.

## Planned capabilities

- Live PR and issue status, code-review feedback, CI, and merge conflicts.
- Concrete testing entry points, expected behavior, and space for exploratory notes.
- Local workspace selection and visible startup/stop logs.
- Commit-specific testing records with screenshots and reproduction steps.
- An explicit preview before actions that commit, push, publish feedback, or create PRs.
- Demo data so the product can be explored without connecting a private repository.

A successful CI run and a passing human check are separate pieces of evidence. Neither implies that required production configuration or alert delivery has been verified.

## Status

Project foundation. The application is not implemented yet.

See [the first-version plan](PLAN.md). This repository contains no credentials, private repository snapshots, or personal workstation paths.

## License

[MIT](LICENSE).
