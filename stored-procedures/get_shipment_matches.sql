CREATE OR REPLACE FUNCTION get_shipment_matches()
RETURNS TABLE (
    match_id UUID,
    schedule_id UUID,
    request_id UUID,
    matched_at TIMESTAMP,
    status VARCHAR
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY 
    SELECT 
        s.matchid, s.scheduleid, s.requestid, s.matchedat, s.status
    FROM public."shipmentmatches" s;
END;
$$;
