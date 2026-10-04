import subprocess
from pathlib import Path
from typing import List, Tuple
import logging
from app.database.repository import repository

logger = logging.getLogger("summit.git")


class GitService:
    """Manages local git repositories inside project workspace directories."""

    def _run_git(self, workspace_path: Path, args: List[str]) -> Tuple[int, str]:
        try:
            res = subprocess.run(
                ["git"] + args,
                cwd=str(workspace_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace"
            )
            return res.returncode, (res.stdout + res.stderr).strip()
        except FileNotFoundError:
            return -1, "Git binary not found on system path."
        except Exception as e:
            return -1, f"Git execution error: {str(e)}"

    def ensure_git_repo(self, workspace_path: Path):
        git_dir = workspace_path / ".git"
        if not git_dir.exists():
            self._run_git(workspace_path, ["init"])
            self._run_git(workspace_path, ["config", "user.name", "Summit AI"])
            self._run_git(workspace_path, ["config", "user.email", "summit@workspace.local"])
            # Initial commit
            self._run_git(workspace_path, ["add", "-A"])
            self._run_git(workspace_path, ["commit", "-m", "Initial workspace setup"])

    def get_status(self, workspace_path: Path) -> dict:
        self.ensure_git_repo(workspace_path)
        code, out = self._run_git(workspace_path, ["status", "--porcelain", "-b"])
        if code != 0:
            return {"branch": "main", "modified": [], "staged": [], "untracked": [], "is_clean": True}

        lines = out.splitlines()
        branch = "main"
        modified, staged, untracked = [], [], []

        for line in lines:
            if line.startswith("##"):
                branch_info = line[2:].strip().split("...")[0]
                branch = branch_info if branch_info else "main"
                continue
            if len(line) >= 3:
                x, y = line[0], line[1]
                path = line[3:].strip()
                if x in ["M", "A", "D", "R"]:
                    staged.append(path)
                if y == "M":
                    modified.append(path)
                elif line.startswith("??"):
                    untracked.append(path)

        is_clean = not (modified or staged or untracked)
        return {
            "branch": branch,
            "modified": modified,
            "staged": staged,
            "untracked": untracked,
            "is_clean": is_clean
        }

    def get_diff(self, workspace_path: Path) -> str:
        self.ensure_git_repo(workspace_path)
        # Get unstaged diff
        _, diff_unstaged = self._run_git(workspace_path, ["diff"])
        # Get staged diff
        _, diff_staged = self._run_git(workspace_path, ["diff", "--cached"])

        full_diff = ""
        if diff_staged:
            full_diff += "--- STAGED CHANGES ---\n" + diff_staged + "\n\n"
        if diff_unstaged:
            full_diff += "--- UNSTAGED CHANGES ---\n" + diff_unstaged

        return full_diff or "No changes detected."

    def create_checkpoint(self, project_id: str, workspace_path: Path, message: str) -> dict:
        self.ensure_git_repo(workspace_path)
        self._run_git(workspace_path, ["add", "-A"])
        code, out = self._run_git(workspace_path, ["commit", "-m", message])

        # Get current commit hash
        _, commit_hash = self._run_git(workspace_path, ["rev-parse", "--short", "HEAD"])
        if code != 0 and "nothing to commit" in out.lower():
            commit_hash = commit_hash or "clean"

        record = repository.save_git_checkpoint(project_id, commit_hash or "unknown", message)
        return record

    def list_checkpoints(self, project_id: str) -> List[dict]:
        return repository.get_git_checkpoints(project_id)


git_service = GitService()
