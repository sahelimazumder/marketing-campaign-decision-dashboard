# Calculation and product decisions

- Fixed four-channel contract for version 1. Uploads require the four documented files; arbitrary spreadsheets and automatic column mapping are future work.
- Acquisition window filters lead creation and spend dates. Outcomes use a separate inclusive cutoff. Revenue is linked through the acquisition lead and includes orders from the won date through that cutoff, net of refunds in the source.
- Refund dates are absent from the contract. Refund amounts reflect the supplied snapshot, so historical cutoffs cannot reconstruct when a refund was known. The dataset is not an accounting ledger.
- The won timestamp defines acquisition. new_customer is retained as source metadata, not summed to count customers. Each customer may have only one acquisition lead; unmatched orders do not create acquisitions.
- Spend, leads and order revenue aggregate separately before joining. SQL view campaign_summary_v1 implements reporting. Cohort totals include unattributed leads when selected.
- Zero denominators return unavailable. A zero-spend channel with customers has observed CAC zero but is ineligible for scenario estimates: no assumption of infinitely scalable free acquisition.
- Scenario = allocated spend / observed channel CAC. Efficiency sensitivity is an acquisition multiplier (0.8, 1, 1.2), not a statistical confidence interval. No optimization or causal forecast is claimed.
- User-provided net revenue and delivery cost per customer share one stated value horizon. Contribution excludes fixed overhead and tax. Return denominator is marketing spend. Break-even CAC is revenue per customer less delivery cost.
- SQLite is rebuilt in memory for each load. Uploaded files and scenarios are session-local. Raw demo files are never replaced.
- Pending optional outcomes and unattributed campaigns are explicitly retained. Structural problems reject the load rather than silently fixing records. There is no generic quarantine/review workflow in this first version.
