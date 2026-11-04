
  
    

  create  table "project_ads_db"."public"."ads_metrics_hourly__dbt_tmp"
  
  
    as
  
  (
    

WITH cleaned_data AS (
    SELECT 
        toStartOfHour(event_time) as hour,
        device_type,
        placement,
        count(event_id) as total_impressions,
        sum(CASE WHEN is_click = true THEN 1 ELSE 0 END) as total_clicks,
        avg(page_load_time_ms) as avg_page_load_ms,
        avg(bid_price) as avg_bid_price
    FROM "project_ads_db"."public"."stg_speed_metrics" -- Ссылка на предыдущую модель!
    GROUP BY hour, device_type, placement
)

SELECT 
    hour,
    device_type,
    placement,
    total_impressions,
    total_clicks,
    CAST(avg_page_load_ms AS UInt32) as avg_page_load_ms,
    CAST(avg_bid_price AS Float32) as avg_bid_price,
    CAST((total_clicks / total_impressions) * 100 AS Float32) as ctr_percentage
FROM cleaned_data
  );
  