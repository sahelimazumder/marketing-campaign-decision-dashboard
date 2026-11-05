# Data dictionary

All CSV fields load as text. Currency is INR, at most two decimals; SQLite holds money as integer paise. IDs must remain strings. CSV row numbers in error messages include the header.

| Table / grain | Fields |
|---|---|
| campaigns / one campaign | campaign_id unique; campaign_name; channel in Paid Search, Paid Social, Email, Partner; start_date, end_date as YYYY-MM-DD |
| spend_daily / campaign-day | campaign_id foreign key; spend_date YYYY-MM-DD; spend_amount >=0; campaign_id + spend_date unique |
| leads / acquisition lead | lead_id unique; campaign_id nullable foreign key; created_at ISO timestamp; qualified_at nullable ISO timestamp; won_at nullable ISO timestamp; customer_id nullable unique when populated |
| orders / completed order | order_id unique; customer_id; order_date YYYY-MM-DD; gross_amount >=0; refund_amount between 0 and gross_amount; new_customer 0 or 1 |

Timestamp strings use a consistent local, timezone-naive convention. won_at and customer_id must appear together; outcomes cannot precede lead creation. Customer acquisition is defined by the unique linked lead and won_at, not the number of orders or new_customer flags. Orders without matching acquisition leads are reported and excluded from cohort-attributed revenue; they may belong to pre-existing customers.

Blank qualification means no observed qualification; blank won_at/customer means no observed acquisition. Blank campaign is explicitly unattributed, not imputed. Required missing values reject the dataset. No contact fields are collected or exported. Extra upload columns are not loaded into SQLite or exported.
