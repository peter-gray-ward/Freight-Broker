CREATE OR REPLACE FUNCTION insert_freighter_schedule(
    p_freighter_id UUID,
    p_departure_city VARCHAR,
    p_departure_lat DECIMAL(9,6),
    p_departure_lng DECIMAL(9,6),
    p_arrival_city VARCHAR,
    p_arrival_lat DECIMAL(9,6),
    p_arrival_lng DECIMAL(9,6),
    p_departure_date TIMESTAMP,
    p_arrival_date TIMESTAMP,
    p_max_load_kg DECIMAL(10,2),
    p_available_kg DECIMAL(10,2),
    p_status VARCHAR
) RETURNS TABLE (
    scheduleid UUID,
    freighterid UUID,
    departurecity VARCHAR,
    departurelat DECIMAL(9,6),
    departurelng DECIMAL(9,6),
    arrivalcity VARCHAR,
    arrivallat DECIMAL(9,6),
    arrivallng DECIMAL(9,6),
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
    INSERT INTO public."freighterschedules" (
        FreighterID, DepartureCity, DepartureLat, DepartureLng, 
        ArrivalCity, ArrivalLat, ArrivalLng, 
        DepartureDate, ArrivalDate, 
        MaxLoadKg, AvailableKg, Status
    ) VALUES (
        p_freighter_id, p_departure_city, p_departure_lat, p_departure_lng,
        p_arrival_city, p_arrival_lat, p_arrival_lng,
        p_departure_date, p_arrival_date,
        p_max_load_kg, p_available_kg, p_status
    )
    RETURNING 
        freighterschedules.ScheduleID, freighterschedules.FreighterID, freighterschedules.DepartureCity, freighterschedules.DepartureLat, freighterschedules.DepartureLng,
        freighterschedules.ArrivalCity, freighterschedules.ArrivalLat, freighterschedules.ArrivalLng,
        freighterschedules.DepartureDate, freighterschedules.ArrivalDate, 
        freighterschedules.MaxLoadKg, freighterschedules.AvailableKg, freighterschedules.Status, freighterschedules.CreatedAt, freighterschedules.LastUpdated;
END;
$$;
