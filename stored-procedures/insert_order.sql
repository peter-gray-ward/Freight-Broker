CREATE OR REPLACE FUNCTION insert_order(
    p_client_id UUID,
    p_request_id UUID,
    p_schedule_id UUID,
    p_status VARCHAR
) RETURNS TABLE (
    order_id UUID,
    client_id UUID,
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
    INSERT INTO public."ShipmentMatches" (
        RequestID, ScheduleID, MatchedAt, Status
    ) VALUES (
        p_request_id, p_schedule_id, NOW(), p_status
    )
    RETURNING 
        MatchID AS order_id, RequestID, ScheduleID, Status, MatchedAt AS CreatedAt, LastUpdated;
END;
$$;
