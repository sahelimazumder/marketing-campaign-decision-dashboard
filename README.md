# Marketing Campaign Decision Dashboard

A local decision-support dashboard for a fictional education business. It connects campaign spending to lead quality, customer acquisition and attributed revenue, then lets a manager explore a proposed marketing budget. The project uses synthetic data and does not claim real-world business results.

## Project summary

- **Business question:** Which marketing channels and campaigns bring qualified leads and customers at an acceptable acquisition cost, and what might a proposed allocation deliver under stated assumptions?
- **Dashboard:** Three interactive pages cover performance, campaign comparison and a manual budget scenario. Users can load a compatible dataset using four CSV templates.
- **Analysis:** Acquisition cohorts, qualification rate, cost per lead, customer acquisition cost, attributed net revenue and return on ad spend are calculated from validated source data.
- **Scenario:** Allocations are divided by historical channel CAC; user-provided customer revenue and delivery cost assumptions support sensitivity cases and an estimated return on marketing spend. These are illustrative scenarios, not causal forecasts or an optimisation model.
- **Tools:** Python, Streamlit, pandas, SQLite, Plotly and pytest. A Power BI build guide is included; no PBIX has been created.
- **Provenance:** The demo data is synthetic. The initial implementation was AI-assisted and reviewed iteratively. See the case study and project documentation for definitions and limitations.

## Run on Windows

Use Python 3.13. From this project directory:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python -m streamlit run app.py
.\.venv\Scripts\python -m pytest -q
```

Both demo datasets are bundled. To generate a separate dataset explicitly:

```powershell
python scripts/seed_data.py --output data/my_new_demo --seed 42
```

Existing directories are rejected, never overwritten. Default seed is 42. No runtime network calls are required by application code.

## Use

Choose a demo or upload four UTF-8 CSV files using the downloadable header templates. All money is INR. Review data quality, select an acquisition window and outcome cutoff, then inspect the three reporting pages. Downloads match the active filters. Dataset uploads are held in the local Streamlit session and are not persisted. Budgets remain in session widget state; no saved scenario history is claimed.

Read BUSINESS_BRIEF.md first, then DATA_DICTIONARY.md, DECISIONS.md and POWER_BI_GUIDE.md. See VALIDATION.md for actual verification results. This is a local demo, not a hosted service. No native PBIX is included.

## Structure

`app.py`: interface; `src/model.py`: CSV ingestion, validation, SQLite view and calculations; `scripts/seed_data.py`: reproducible generator; `tests/`: deterministic fixtures; `data/`: two compatible datasets; `sql/`: reference schema and analytical query.
