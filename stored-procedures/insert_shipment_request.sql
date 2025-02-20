CREATE OR REPLACE FUNCTION insert_shipment_request(
    p_client_id UUID,
    p_origin_city VARCHAR,
    p_origin_lat DECIMAL(9,6),
    p_origin_lng DECIMAL(9,6),
    p_destination_city VARCHAR,
    p_destination_lat DECIMAL(9,6),
    p_destination_lng DECIMAL(9,6),
    p_weight_kg DECIMAL(10,2),
    p_special_handling VARCHAR
) RETURNS TABLE (
    request_id UUID,
    client_id UUID,
    origin_city VARCHAR,
    origin_lat DECIMAL(9,6),
    origin_lng DECIMAL(9,6),
    destination_city VARCHAR,
    destination_lat DECIMAL(9,6),
    destination_lng DECIMAL(9,6),
    weight_kg DECIMAL(10,2),
    special_handling VARCHAR,
    status VARCHAR,
    created_at TIMESTAMP,
    last_updated TIMESTAMP
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY 
    INSERT INTO public."ShipmentRequests" (
        ClientID, OriginCity, OriginLat, OriginLng, DestinationCity, DestinationLat, DestinationLng, WeightKg, SpecialHandling, Status
    ) VALUES (
        p_client_id, p_origin_city, p_origin_lat, p_origin_lng, 
        p_destination_city, p_destination_lat, p_destination_lng, 
        p_weight_kg, p_special_handling, 'Pending'
    )
    RETURNING 
        RequestID, ClientID, OriginCity, OriginLat, OriginLng, DestinationCity, DestinationLat, DestinationLng, 
        WeightKg, SpecialHandling, Status, CreatedAt, LastUpdated;
END;
$$;
