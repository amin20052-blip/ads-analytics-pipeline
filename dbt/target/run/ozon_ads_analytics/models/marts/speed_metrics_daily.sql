
  
    

  create  table "project_ads_db"."public"."speed_metrics_daily__dbt_tmp"
  
  
    as
  
  (
    

SELECT 
    CAST(parsed_at AS DATE) AS metric_date,
    url,
    ROUND(AVG(lcp_sec), 2) AS avg_lcp_sec,
    ROUND(AVG(cls), 3) AS avg_cls,
    ROUND(AVG(tbt_sec), 2) AS avg_tbt_sec,
    COUNT(*) AS measurements_count
FROM "project_ads_db"."public"."stg_speed_metrics"
GROUP BY CAST(parsed_at AS DATE), url
ORDER BY metric_date DESC, url
  );
  