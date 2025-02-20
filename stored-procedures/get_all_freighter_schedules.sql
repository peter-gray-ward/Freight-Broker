CREATE OR REPLACE FUNCTION get_all_freighter_schedules()
RETURNS TABLE (
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
    SELECT 
        ScheduleID, FreighterID, DepartureCity, DepartureLat, DepartureLng,
        ArrivalCity, ArrivalLat, ArrivalLng, 
        DepartureDate, ArrivalDate, 
        MaxLoadKg, AvailableKg, Status, CreatedAt, LastUpdated
    FROM public."FreighterSchedules";
END;
$$;
