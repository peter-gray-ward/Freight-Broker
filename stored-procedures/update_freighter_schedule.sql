CREATE OR REPLACE FUNCTION update_freighter_schedule(
    p_schedule_id UUID,
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
    UPDATE public."FreighterSchedules"
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
    WHERE ScheduleID = p_schedule_id
    RETURNING 
        ScheduleID, FreighterID, DepartureCity, DepartureLat, DepartureLng,
        ArrivalCity, ArrivalLat, ArrivalLng, 
        DepartureDate, ArrivalDate, 
        MaxLoadKg, AvailableKg, Status, CreatedAt, LastUpdated;
END;
$$;
