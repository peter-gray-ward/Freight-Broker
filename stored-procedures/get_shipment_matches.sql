CREATE OR REPLACE FUNCTION get_shipment_matches(p_request_id UUID)
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
        MatchID, ScheduleID, RequestID, MatchedAt, Status
    FROM public."ShipmentMatches"
    WHERE RequestID = p_request_id;
END;
$$;
