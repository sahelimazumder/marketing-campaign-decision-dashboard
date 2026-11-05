CREATE TABLE "campaigns" (
"campaign_id" TEXT,
  "campaign_name" TEXT,
  "channel" TEXT,
  "start_date" TEXT,
  "end_date" TEXT
);

CREATE TABLE "spend_daily" (
"campaign_id" TEXT,
  "spend_date" TEXT,
  "spend_amount" INTEGER
);

CREATE TABLE "leads" (
"lead_id" TEXT,
  "campaign_id" TEXT,
  "created_at" TEXT,
  "qualified_at" TEXT,
  "won_at" TEXT,
  "customer_id" TEXT
);

CREATE TABLE "orders" (
"order_id" TEXT,
  "customer_id" TEXT,
  "order_date" TEXT,
  "gross_amount" INTEGER,
  "refund_amount" INTEGER,
  "new_customer" TEXT
);

CREATE TABLE report_window (start_date TEXT, end_date TEXT, cutoff TEXT);

CREATE VIEW campaign_summary_v1 AS
    WITH cohort AS (
      SELECT l.* FROM leads l, report_window w
      WHERE substr(l.created_at,1,10) BETWEEN w.start_date AND w.end_date
    ), s AS (
      SELECT campaign_id, SUM(spend_amount) spend FROM spend_daily, report_window w
      WHERE spend_date BETWEEN w.start_date AND w.end_date GROUP BY campaign_id
    ), outcomes AS (
      SELECT c.campaign_id,COUNT(*) leads,
      SUM(CASE WHEN qualified_at != '' AND substr(qualified_at,1,10)<=w.cutoff THEN 1 ELSE 0 END) qualified,
      SUM(CASE WHEN won_at != '' AND substr(won_at,1,10)<=w.cutoff THEN 1 ELSE 0 END) customers
      FROM cohort c, report_window w GROUP BY c.campaign_id
    ), revenue AS (
      SELECT c.campaign_id,SUM(o.gross_amount-o.refund_amount) revenue
      FROM cohort c JOIN orders o ON o.customer_id=c.customer_id, report_window w
      WHERE c.customer_id!='' AND c.won_at!='' AND substr(c.won_at,1,10)<=w.cutoff
      AND o.order_date BETWEEN substr(c.won_at,1,10) AND w.cutoff GROUP BY c.campaign_id
    ), all_campaigns AS (
      SELECT campaign_id,campaign_name,channel FROM campaigns
      UNION ALL SELECT '', 'Unattributed', 'Unattributed'
    )
    SELECT a.*,COALESCE(s.spend,0)/100.0 spend,COALESCE(l.leads,0) leads,
    COALESCE(l.qualified,0) qualified,COALESCE(l.customers,0) customers,
    COALESCE(r.revenue,0)/100.0 revenue
    FROM all_campaigns a LEFT JOIN s USING(campaign_id)
    LEFT JOIN outcomes l USING(campaign_id) LEFT JOIN revenue r USING(campaign_id);