-- One-time migration: apply 180-day partition expiration to the existing
-- live tables in BigQuery. CREATE TABLE IF NOT EXISTS in the individual
-- schema files won't touch tables that already exist, so run this once
-- against the live dataset (e.g. `bq query --use_legacy_sql=false < bq/schema/apply_retention.sql`,
-- or paste into the BigQuery console) to bring them in line.
--
-- Partitions older than 180 days will be dropped automatically by BigQuery
-- going forward - no DAG or scheduled job needed.
--
-- data_health is intentionally excluded: it's a small upserted status
-- table (one row per source), not an append-only event log, so expiring
-- its partition would risk deleting the current freshness status rather
-- than pruning growth.

ALTER TABLE `thub-10b72.marketing_demo.fact_events`
SET OPTIONS (partition_expiration_days = 180);

ALTER TABLE `thub-10b72.marketing_demo.fact_ad_spend`
SET OPTIONS (partition_expiration_days = 180);

ALTER TABLE `thub-10b72.marketing_demo.fact_attribution`
SET OPTIONS (partition_expiration_days = 180);

ALTER TABLE `thub-10b72.marketing_demo.fact_campaign_metrics`
SET OPTIONS (partition_expiration_days = 180);

ALTER TABLE `thub-10b72.marketing_demo.fact_orders`
SET OPTIONS (partition_expiration_days = 180);
