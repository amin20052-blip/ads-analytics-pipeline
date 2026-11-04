
  create view "project_ads_db"."public"."asset_ctr_positive__dbt_tmp"
    
    
  as (
    

SELECT 
    event_id,
    event_time,
    user_id,
    product_id,
    placement,
    device_type,
    is_click,
    bid_price,
    page_load_time_ms
FROM public.raw_ad_events
  );