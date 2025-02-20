CREATE OR REPLACE FUNCTION get_order(p_order_id UUID)
RETURNS TABLE (
    order_id UUID,
    request_id UUID,
    schedule_id UUID,
    status VARCHAR,
    created_at TIMESTAMP,
    last_updated TIMESTAMP
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY 
    SELECT 
        MatchID AS order_id, RequestID, ScheduleID, Status, MatchedAt AS CreatedAt, LastUpdated
    FROM public."ShipmentMatches"
    WHERE MatchID = p_order_id;
END;
$$;
