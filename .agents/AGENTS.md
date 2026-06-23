# Agent Rules for Spira Mod Manager

1. **Always Require Implementation Plan Approval**: Before making ANY code changes or file creations/deletions, you must write an implementation plan (updating `implementation_plan.md` or creating a new plan) and wait for the user's explicit approval.
2. **Restricted Git & GitHub Operations**: NEVER stage files, commit changes, or execute `git push` command unless the user explicitly instructs you to perform that action or you have requested and received permission first.
3. **Changelog Maintenance**: After every change to the code or files, a changelog with the current version must be created or edited to add the changes made.
4. **Plugin Release Separation**: Plugins are never included in the release of the mod manager and are hosted separately.
5. **Plugin Changelog Maintenance**: Changes made to plugins must be added to the plugins' respective changelog with its version as well.
6. **Persistent Project Backlog Memory**: Brainstormed ideas, feedback, and proposed future features must be recorded in `backlog.md` in the project root to serve as persistent memory until they are fully completed or explicitly discarded by the user.
7. **Dynamic Path & Working Directory Resolution**: Always dynamically resolve working directories, repository files, and system paths in executable tools, compilers, and launchers instead of using hardcoded paths. This ensures the mod manager compiles, launches, and operates seamlessly when built on public development machines.
8. **Plugin Changelog Isolation**: Changes made to plugins must never be added to the main mod manager application's changelogs (such as `VERSION_future_release.md` or files inside the `changelogs/` folder). Plugin changes are documented strictly in the plugin's own changelog.
