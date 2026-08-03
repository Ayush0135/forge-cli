import json

import git


class GitTools:
    """Git operations using GitPython."""
    
    @staticmethod
    def _get_repo(path: str = ".") -> git.Repo | None:
        try:
            return git.Repo(path, search_parent_directories=True)
        except git.InvalidGitRepositoryError:
            return None

    @staticmethod
    def git_status(path: str = ".") -> str:
        repo = GitTools._get_repo(path)
        if not repo:
            return json.dumps({"error": "Not a git repository"})
            
        status = {
            "branch": repo.active_branch.name if not repo.head.is_detached else "detached",
            "is_dirty": repo.is_dirty(untracked_files=True),
            "untracked": repo.untracked_files,
            "modified": [item.a_path for item in repo.index.diff(None)],
            "staged": [item.a_path for item in repo.index.diff("HEAD")] if repo.head.is_valid() else []
        }
        return json.dumps(status)

    @staticmethod
    def git_diff(path: str = ".", staged: bool = False) -> str:
        repo = GitTools._get_repo(path)
        if not repo:
            return json.dumps({"error": "Not a git repository"})
            
        try:
            diff = repo.git.diff("--staged") if staged else repo.git.diff()
            return json.dumps({"diff": diff})
        except Exception as e:  # noqa: BLE001 - GitPython exposes several runtime command errors.
            return json.dumps({"error": str(e)})

    @staticmethod
    def git_log(path: str = ".", max_count: int = 10) -> str:
        repo = GitTools._get_repo(path)
        if not repo:
            return json.dumps({"error": "Not a git repository"})
            
        try:
            commits = []
            for commit in repo.iter_commits(max_count=max_count):
                commits.append({
                    "hash": commit.hexsha,
                    "author": commit.author.name,
                    "message": commit.message.strip(),
                    "date": commit.committed_datetime.isoformat()
                })
            return json.dumps({"commits": commits})
        except Exception as e:  # noqa: BLE001 - GitPython exposes several runtime command errors.
            return json.dumps({"error": str(e)})

    @staticmethod
    def git_branch(path: str = ".") -> str:
        repo = GitTools._get_repo(path)
        if not repo:
            return json.dumps({"error": "Not a git repository"})
            
        try:
            branches = [h.name for h in repo.heads]
            active = repo.active_branch.name if not repo.head.is_detached else "detached"
            return json.dumps({"active": active, "branches": branches})
        except Exception as e:  # noqa: BLE001 - GitPython exposes several runtime command errors.
            return json.dumps({"error": str(e)})

    @staticmethod
    def git_commit(message: str, path: str = ".") -> str:
        repo = GitTools._get_repo(path)
        if not repo:
            return json.dumps({"error": "Not a git repository"})
            
        try:
            repo.git.add(all=True)
            commit = repo.index.commit(message)
            return json.dumps({"success": True, "hash": commit.hexsha})
        except Exception as e:  # noqa: BLE001 - GitPython exposes several runtime command errors.
            return json.dumps({"error": str(e)})

    @staticmethod
    def git_checkout(branch_or_commit: str, create: bool = False, path: str = ".") -> str:
        repo = GitTools._get_repo(path)
        if not repo:
            return json.dumps({"error": "Not a git repository"})
            
        try:
            if create:
                repo.git.checkout("-b", branch_or_commit)
            else:
                repo.git.checkout(branch_or_commit)
            return json.dumps({"success": True, "checkout": branch_or_commit})
        except Exception as e:  # noqa: BLE001 - GitPython exposes several runtime command errors.
            return json.dumps({"error": str(e)})
