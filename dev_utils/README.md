# Developer Utilities

This directory contains various support scripts, debug tools, and ad-hoc tests for the Anti-Bullying App.

## How to Run

Because these scripts often import from the `app` package (the root of the project), **you must run them from the project root directory** using the `-m` flag (module syntax).

### Examples

**Correct:**
```bash
# Run from the project root (Anti-Bullying_app)
python -m dev_utils.seed_user
python -m dev_utils.test_login
python -m dev_utils.debug_relationships
```

**Incorrect:**
```bash
cd dev_utils
python seed_user.py  # This will likely fail with "ModuleNotFoundError: No module named 'app'"
```

## Contents

- **Seeding Scripts:** `seed_user.py`, `seed_large_db.py`, `seed_parent_surveys.py`, `create_demo_parent.py` (Create data for development)
- **Debug Tools:** `debug_env.py`, `debug_relationships.py`, `check_map_data.py` (Inspect authentications, database states)
- **Tests:** `test_login.py`, `test_password_policy.py`, `test_db_integration.py` (Ad-hoc integration tests)
- **Data Inspection:** `inspect_excel.py`, `read_docx.py` (Utilities for checking data files)
