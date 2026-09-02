# Workspace file resolution

Update `resolve_workspace_path` so callers can resolve files stored within a workspace. It should return the resolved path for valid workspace-relative requests and reject requests outside that workspace.
