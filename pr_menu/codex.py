"""Prepare a known branch workspace and a documented Codex desktop deep link."""
import hashlib
import subprocess
import threading
from pathlib import Path
from urllib.parse import urlencode

WORKSPACE_LOCK = threading.Lock()


def git(repo, *args):
    result = subprocess.run(['git', '-C', str(repo), *args], capture_output=True,
                            text=True, timeout=30)
    if result.returncode:
        # Keep credentials and arbitrary Git output out of the browser response.
        raise ValueError('Git could not prepare this branch. Check its local checkout and permissions.')
    return result.stdout.strip()


def prepare_chat(report, branch, workspace_root):
    if report.get('mode') != 'local':
        raise ValueError('Open in Codex requires a local repository; demo data cannot create workspaces.')
    item = next((b for b in report.get('branches', []) if b['name'] == branch), None)
    if item is None:
        raise ValueError('Choose a branch from the current report.')
    repo = Path(report.get('repo', ''))
    if not repo.is_absolute() or not repo.is_dir():
        raise ValueError('The report must name an existing absolute repository path.')
    repo = repo.resolve()
    if Path(git(repo, 'rev-parse', '--show-toplevel')).resolve() != repo:
        raise ValueError('The report repository must be a Git workspace root.')
    # Verify a full local branch ref. Never accept command options or revisions.
    ref = 'refs/heads/' + branch
    git(repo, 'check-ref-format', ref)
    git(repo, 'show-ref', '--verify', ref)
    with WORKSPACE_LOCK:
        workspace = None
        for block in git(repo, 'worktree', 'list', '--porcelain').split('\n\n'):
            fields = dict(line.partition(' ')[::2] for line in block.splitlines())
            path = Path(fields.get('worktree', ''))
            if fields.get('branch') == ref and path.is_dir():
                # Recheck live Git state instead of trusting the snapshot path.
                if git(path, 'symbolic-ref', '--quiet', 'HEAD') == ref:
                    workspace = path.resolve()
                    break
        created = workspace is None
        if created:
            identity = hashlib.sha256((str(repo) + '\0' + branch).encode()).hexdigest()[:20]
            workspace = Path(workspace_root).resolve() / identity
            workspace.parent.mkdir(parents=True, exist_ok=True)
            if workspace.exists():
                raise ValueError('The managed workspace path is occupied. Review it before retrying.')
            git(repo, 'worktree', 'add', str(workspace), branch)
    lines = [f'Help me dogfood and review branch {branch}.',
             f'The workspace should be {workspace}. Verify the current branch before making changes.',
             'Preserve any existing uncommitted work. Start by inspecting the change and proposing concrete hands-on checks.']
    if (item.get('pr') or {}).get('url'):
        lines.append('Pull request: ' + item['pr']['url'])
    if item.get('testChecklist'):
        lines.append('Suggested testing context (verify against the code): ' + item['testChecklist'])
    lines.append('Do not commit, push, merge, or publish feedback unless I ask.')
    prompt = '\n\n'.join(lines)
    return {'url': 'codex://new?' + urlencode({'path': str(workspace), 'prompt': prompt}),
            'workspace': str(workspace), 'created': created, 'branch': branch}
