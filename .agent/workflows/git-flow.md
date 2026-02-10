---
description: Project Git Workflow Policy
---
// turbo-all
# Git Workflow Policy

All development work for this project must follow this workflow:

1. **Base Branch**: The primary development branch is `dev`.
2. **Branching**: For any new feature or fix, create a new branch from `dev` named:
   - `feat/<change>` for features
   - `fix/<change>` for bug fixes (inherited best practice)
3. **Drafting Changes**: Work on your feature/fix branch.
4. **Integration**:
   - Use `git rebase dev` to keep your branch up to date with the latest changes from `dev`.
   - Ensure all commits are clean and documented.
5. **Pull Requests**:
   - Create a Pull Request (PR) for every change.
   - The PR target must be the `dev` branch.
6. **Merging**: PRs should be merged into `dev` after review and verification.

*Note: This policy ensures a clean commit history and consistent integration process.*
