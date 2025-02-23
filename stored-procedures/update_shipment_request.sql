CREATE OR REPLACE FUNCTION update_shipment_request(
    p_request_id UUID,
    p_client_id UUID,
    p_origin_city VARCHAR,
    p_origin_lat DOUBLE PRECISION,
    p_origin_lng DOUBLE PRECISION,
    p_destination_city VARCHAR,
    p_destination_lat DOUBLE PRECISION,
    p_destination_lng DOUBLE PRECISION,
    p_weight_kg DECIMAL(10,2),
    p_special_handling VARCHAR,
    p_status VARCHAR
) RETURNS TABLE (
    requestid UUID,
    clientid UUID,
    origincity VARCHAR,
    originlat DOUBLE PRECISION,
    originlng DOUBLE PRECISION,
    destinationcity VARCHAR,
    destinationlat DOUBLE PRECISION,
    destinationlng DOUBLE PRECISION,
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
    UPDATE public."shipmentrequests"
    SET 
        ClientID = p_client_id,
        OriginCity = p_origin_city,
        OriginLat = p_origin_lat,
        OriginLng = p_origin_lng,
        DestinationCity = p_destination_city,
        DestinationLat = p_destination_lat,
        DestinationLng = p_destination_lng,
        WeightKg = p_weight_kg,
        SpecialHandling = p_special_handling,
        Status = p_status,
        LastUpdated = NOW()
    WHERE shipmentrequests.RequestID = p_request_id
    RETURNING 
        shipmentrequests.RequestID, shipmentrequests.ClientID, shipmentrequests.OriginCity, shipmentrequests.OriginLat, shipmentrequests.OriginLng, shipmentrequests.DestinationCity, shipmentrequests.DestinationLat, shipmentrequests.DestinationLng, shipmentrequests.
        WeightKg, shipmentrequests.SpecialHandling, shipmentrequests.Status, shipmentrequests.CreatedAt, shipmentrequests.LastUpdated;
END;
$$;