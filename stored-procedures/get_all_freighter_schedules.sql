CREATE OR REPLACE FUNCTION get_all_freighter_schedules()
RETURNS TABLE (
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
    SELECT 
        freighterschedules.ScheduleID, freighterschedules.FreighterID, freighterschedules.DepartureCity, freighterschedules.DepartureLat, freighterschedules.DepartureLng,
        freighterschedules.ArrivalCity, freighterschedules.ArrivalLat, freighterschedules.ArrivalLng, 
        freighterschedules.DepartureDate, freighterschedules.ArrivalDate,
        freighterschedules.MaxLoadKg, freighterschedules.AvailableKg, freighterschedules.Status, freighterschedules.CreatedAt, freighterschedules.LastUpdated
    FROM public."freighterschedules";
END;
$$;
