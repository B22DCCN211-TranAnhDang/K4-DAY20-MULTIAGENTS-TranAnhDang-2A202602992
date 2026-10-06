---
name: validate-file-paths
description: Use to ensure that all required file paths are valid before execution.
---
# Validate File Paths

1. Check that all file paths exist using appropriate file system functions (e.g., os.path.exists).
2. Log an error message if any required file paths are missing before proceeding with operations.
3. Implement fallback mechanisms or prompts to handle missing files gracefully.