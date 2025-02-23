CREATE OR REPLACE FUNCTION update_freighter_schedule(
    p_freighter_id UUID,
    p_departure_city VARCHAR,
    p_departure_lat DOUBLE PRECISION,
    p_departure_lng DOUBLE PRECISION,
    p_arrival_city VARCHAR,
    p_arrival_lat DOUBLE PRECISION,
    p_arrival_lng DOUBLE PRECISION,
    p_departure_date TIMESTAMP,
    p_arrival_date TIMESTAMP,
    p_max_load_kg DECIMAL(10,2),
    p_available_kg DECIMAL(10,2),
    p_status VARCHAR
) RETURNS TABLE (
    scheduleid UUID,
    freighterid UUID,
    departurecity VARCHAR,
    departurelat DOUBLE PRECISION,
    departurelng DOUBLE PRECISION,
    arrivalcity VARCHAR,
    arrivallat DOUBLE PRECISION,
    arrivallng DOUBLE PRECISION,
    departuredate TIMESTAMP,
    arrivaldate TIMESTAMP,
    maxloadkg DECIMAL(10,2),
    availablekg DECIMAL(10,2),
    status VARCHAR,
    createdat TIMESTAMP,
    lastupdated TIMESTAMP
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    UPDATE public."freighterschedules"
    SET 
        DepartureCity = p_departure_city,
        DepartureLat = p_departure_lat,
        DepartureLng = p_departure_lng,
        ArrivalCity = p_arrival_city,
        ArrivalLat = p_arrival_lat,
        ArrivalLng = p_arrival_lng,
        DepartureDate = p_departure_date,
        ArrivalDate = p_arrival_date,
        MaxLoadKg = p_max_load_kg,
        AvailableKg = p_available_kg,
        Status = p_status,
        LastUpdated = NOW()
    WHERE freighterschedules.FreighterID = p_freighter_id
    RETURNING 
        freighterschedules.ScheduleID, freighterschedules.FreighterID, freighterschedules.DepartureCity, freighterschedules.DepartureLat, freighterschedules.DepartureLng,
        freighterschedules.ArrivalCity, freighterschedules.ArrivalLat, freighterschedules.ArrivalLng, 
        freighterschedules.DepartureDate, freighterschedules.ArrivalDate, 
        freighterschedules.MaxLoadKg, freighterschedules.AvailableKg, freighterschedules.Status, freighterschedules.CreatedAt, freighterschedules.LastUpdated;
END;
$$;
