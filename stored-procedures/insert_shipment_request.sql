CREATE OR REPLACE FUNCTION insert_shipment_request(
    p_client_id UUID,
    p_origin_city VARCHAR,
    p_origin_lat DECIMAL(9,6),
    p_origin_lng DECIMAL(9,6),
    p_destination_city VARCHAR,
    p_destination_lat DECIMAL(9,6),
    p_destination_lng DECIMAL(9,6),
    p_weight_kg DECIMAL(10,2),
    p_special_handling VARCHAR,
    p_status VARCHAR
) RETURNS TABLE (
    requestid UUID,
    clientid UUID,
    origincity VARCHAR,
    originlat DECIMAL(9,6),
    originlng DECIMAL(9,6),
    destinationcity VARCHAR,
    destinationlat DECIMAL(9,6),
    destinationlng DECIMAL(9,6),
    weightkg DECIMAL(10,2),
    specialhandling VARCHAR,
    status VARCHAR,
    createdat TIMESTAMP,
    lastupdated TIMESTAMP
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY 
    INSERT INTO public."shipmentrequests" (
        ClientID, OriginCity, OriginLat, OriginLng, DestinationCity, DestinationLat, DestinationLng, WeightKg, SpecialHandling, Status
    ) VALUES (
        p_client_id, p_origin_city, p_origin_lat, p_origin_lng, 
        p_destination_city, p_destination_lat, p_destination_lng, 
        p_weight_kg, p_special_handling, p_status
    )
    RETURNING 
        shipmentrequests.RequestID, shipmentrequests.ClientID, shipmentrequests.OriginCity, shipmentrequests.OriginLat, shipmentrequests.OriginLng, shipmentrequests.DestinationCity, shipmentrequests.DestinationLat, shipmentrequests.DestinationLng, shipmentrequests.
        WeightKg, shipmentrequests.SpecialHandling, shipmentrequests.Status, shipmentrequests.CreatedAt, shipmentrequests.LastUpdated;
END;
$$;
