# Power BI companion build guide

No native PBIX has been created. Use data/demo CSVs as the clean source tables; export filtered campaign_summary and monthly_cohorts from the app to reproduce verified reports.

1. Import campaigns, spend_daily, leads and orders through Power Query. Set IDs to Text, date-only columns to Date, timestamps to Date/Time, money to Fixed Decimal. Preserve blank campaign as an explicit unattributed category if including it in channel slicers.
2. Model campaigns (1) → spend_daily (*) and campaigns (1) → leads (*) using campaign_id, single direction. A customer bridge with distinct nonblank leads.customer_id links (1) to orders (*) and (1) to the acquisition lead (1). Avoid bidirectional fact-to-fact filtering.
3. For exact parity first import the application's campaign summary export as a standalone reporting table; do not connect it to facts and sum both. Display the exported acquisition window and cutoff in a subtitle. Refresh exports when changing those windows. Dynamic cohort cutoffs require disconnected date selectors and explicit fact filtering, not a single shared date slicer.
4. On that standalone reporting table, proposed DAX measures are:

```dax
Spend INR = SUM(campaign_summary[spend])
Leads = SUM(campaign_summary[leads])
Qualified = SUM(campaign_summary[qualified])
Customers = SUM(campaign_summary[customers])
Net Revenue = SUM(campaign_summary[revenue])
CPL = DIVIDE([Spend INR], [Leads])
Qualification Rate = DIVIDE([Qualified], [Leads])
CAC = DIVIDE([Spend INR], [Customers])
ROAS = DIVIDE([Net Revenue], [Spend INR])
```

5. Overview: five volume/value cards, efficiency measures, channel bars, monthly cohort line. Campaign page: spend/customer scatter, sortable summary table. Scenario page: use the exported budget_scenarios table with case, acquisitions, revenue, contribution and return; label it as a snapshot with assumptions. Interactive manual channel allocations remain in Streamlit for version 1.
6. Verify the manual fixture and reconcile totals to the app before presenting any Power BI figures. Never average campaign CAC or ROAS to get an overall measure: divide summed numerators by summed denominators.
