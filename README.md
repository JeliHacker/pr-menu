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

## Run it

Requires Python 3.10 or newer. No package installation is needed.

```sh
git clone https://github.com/JeliHacker/pr-menu.git
cd pr-menu
make dev
```

Open **http://localhost:4317**. Stop the server with **Ctrl+C**.

A fresh clone shows fictional demo data. To always show the demo, run:

```sh
python3 -m pr_menu --demo
```

Choose another port with `python3 -m pr_menu --port 4318`.

## Use the menu

1. Select **Review** in the category filter.
2. Read a branch's purpose, checklist, and verification notes.
3. Use **Copy startup command**, inspect the command, and paste it into a terminal. Commands may stop apps on the project's development ports.
4. Visit its test-page links. Change **App URL** if your application runs somewhere other than localhost:3000.
5. Use **Open in Codex** to open a new desktop chat in this branch’s workspace. It reuses an existing checkout of the branch or creates an isolated worktree under `.pr-menu/workspaces/`. Codex opens with a review prompt; press Send when ready. It does not install dependencies or copy environment files. Codex desktop and the `codex://` handler must be installed.
6. Use **Create PR** to copy a commit/push/PR command. It stages all non-ignored changes; inspect it before running. It opens an existing PR when available.

Startup and Create PR buttons only copy shell commands. Open in Codex runs a fixed set of Git commands to resolve the selected local branch and, if necessary, create a worktree. It never runs a command from the report, switches an existing checkout, sends the chat prompt, or launches an agent automatically. Requests require the local page origin and an action token.

The chat links use the [official desktop deep-link format](https://learn.chatgpt.com/docs/app/commands).

## Local snapshots

The current version displays snapshots; it does not discover repositories or query GitHub automatically. **Reload snapshot** rereads the file, not GitHub.

Put a report matching the structure of [demo.json](demo.json) in `.pr-menu/inventory.json`. This directory is ignored by Git. Refresh the dashboard after replacing that file. Never commit a personal snapshot or environment files.

The original DCF dashboard and its snapshot have been imported locally on the initial developer's machine. Other clones use demo data unless they supply their own snapshot.

## Test

```sh
make test
```

## Status

The original HTML dashboard has been ported into a dependency-free local application. Filters, test links, snapshot reload, and copyable commands work. Live GitHub/Git discovery, persisted dogfooding results, and approved command execution are future work.

See [the first-version plan](PLAN.md). This repository contains no credentials, private repository snapshots, or personal workstation paths.

## License

[MIT](LICENSE).
