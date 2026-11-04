
  create view "project_ads_db"."public"."stg_speed_metrics__dbt_tmp"
    
    
  as (
    

SELECT 
    id,
    url,
    ROUND(lcp_ms / 1000.0, 2) AS lcp_sec,
    ROUND(fcp_ms / 1000.0, 2) AS fcp_sec,
    cls,
    ROUND(tbt_ms / 1000.0, 2) AS tbt_sec,
    parsed_at
FROM public.raw_speed_metrics
  );