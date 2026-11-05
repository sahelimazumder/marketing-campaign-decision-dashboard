# Verification record

Verified 5 November 2026 on Windows, Python 3.13.12, using workspace-local dependencies pinned in requirements.txt.

- `python scripts/seed_data.py --output data/demo`: passed; seed 42.
- `python scripts/seed_data.py --output data/second_demo --seed 73`: passed.
- `python -m pytest -q`: **10 passed in 8.37 seconds**. Includes the hand-calculated fixture (CPL 50, qualification 25%, CAC 500, ROAS 3), repeat orders, zero/empty denominators, duplicate IDs, foreign keys, malformed dates, excessive refunds, duplicate acquisition customers, outcome cutoff, channel filtering, allocation validation and export round-trip.
- Streamlit AppTest opened all three pages, switched to second demo and reached the incomplete-upload state without application exceptions.
- Streamlit testing needed execution outside the sandbox because Windows event-loop socket creation was blocked inside it. Initial sandbox runs stalled before application execution; the subsequent complete run passed.

Limits: automated page execution is not a visual screenshot review. A full browser upload interaction, clean virtual-environment install, and native Power BI parity validation have not been performed. No PBIX is included. Scenario edits and uploaded datasets are not persisted between sessions.
