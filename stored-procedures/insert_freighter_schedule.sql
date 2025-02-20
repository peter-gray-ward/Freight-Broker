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
    schedule_id UUID,
    freighter_id UUID,
    departure_city VARCHAR,
    departure_lat DECIMAL(9,6),
    departure_lng DECIMAL(9,6),
    arrival_city VARCHAR,
    arrival_lat DECIMAL(9,6),
    arrival_lng DECIMAL(9,6),
    departure_date TIMESTAMP,
    arrival_date TIMESTAMP,
    max_load_kg DECIMAL(10,2),
    available_kg DECIMAL(10,2),
    status VARCHAR,
    created_at TIMESTAMP,
    last_updated TIMESTAMP
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY 
    INSERT INTO public."FreighterSchedules" (
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
        ScheduleID, FreighterID, DepartureCity, DepartureLat, DepartureLng,
        ArrivalCity, ArrivalLat, ArrivalLng, 
        DepartureDate, ArrivalDate, 
        MaxLoadKg, AvailableKg, Status, CreatedAt, LastUpdated;
END;
$$;
