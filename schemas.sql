CREATE TABLE IF NOT EXISTS Users (
    UserID        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    Name          VARCHAR(255) NOT NULL,
    Email         VARCHAR(255) UNIQUE NOT NULL,
    PasswordHash  VARCHAR(255) NOT NULL,
    Role          VARCHAR(20) CHECK (Role IN ('Supplier', 'Freighter', 'Admin')),
    CreatedAt     TIMESTAMP DEFAULT NOW()
);

DROP FUNCTION IF EXISTS insert_user_with_id;
DROP FUNCTION IF EXISTS get_all_freighter_schedules;
DROP FUNCTION IF EXISTS get_shipment_matches;
DROP FUNCTION IF EXISTS insert_user;
DROP FUNCTION IF EXISTS insert_shipment_request;
DROP FUNCTION IF EXISTS update_freighter_schedule;
DROP FUNCTION IF EXISTS get_shipment_matches;


DROP TABLE IF EXISTS ShipmentMatches;
DROP TABLE IF EXISTS FreighterSchedules;
DROP TABLE IF EXISTS ShipmentRequests;

CREATE TABLE FreighterSchedules (
    ScheduleID     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    FreighterID    UUID REFERENCES Users(UserID) ON DELETE CASCADE,
    DepartureCity  VARCHAR(255),
    DepartureLat   DOUBLE PRECISION,  -- Latitude with 6 decimal places
    DepartureLng   DOUBLE PRECISION,  -- Longitude with 6 decimal places
    ArrivalCity    VARCHAR(255),
    ArrivalLat     DOUBLE PRECISION,  -- Latitude with 6 decimal places
    ArrivalLng     DOUBLE PRECISION,  -- Longitude with 6 decimal places
    DepartureDate  TIMESTAMP,
    ArrivalDate    TIMESTAMP,
    MaxLoadKg      DECIMAL(10,2),
    AvailableKg    DECIMAL(10,2),
    Status         VARCHAR(20) CHECK (Status IN ('available', 'in transit', 'completed')),
    CreatedAt      TIMESTAMP DEFAULT NOW(),
    LastUpdated    TIMESTAMP DEFAULT NOW()  -- Optimistic Locking
);

CREATE TABLE ShipmentRequests (
    RequestID       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ClientID        UUID REFERENCES Users(UserID) ON DELETE CASCADE,
    OriginCity      VARCHAR(255),
    OriginLat       DOUBLE PRECISION,  -- Latitude
    OriginLng       DOUBLE PRECISION,  -- Longitude
    DestinationCity VARCHAR(255),
    DestinationLat  DOUBLE PRECISION,  -- Latitude
    DestinationLng  DOUBLE PRECISION,  -- Longitude
    WeightKg        DECIMAL(10,2),
    SpecialHandling VARCHAR(255),
    Status          VARCHAR(20) CHECK (Status IN ('pending', 'matched', 'completed')),
    CreatedAt       TIMESTAMP DEFAULT NOW(),
    LastUpdated     TIMESTAMP DEFAULT NOW()  -- Optimistic Locking
);

CREATE TABLE ShipmentMatches (
    MatchID       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ClientID      UUID,
    FreighterID   UUID,
    RequestID     UUID,
    ScheduleID    UUID,
    MatchedAt     TIMESTAMP DEFAULT NOW(),
    Status        VARCHAR(20) CHECK (Status IN ('matched', 'completed')),
    LastUpdated   TIMESTAMP DEFAULT NOW()  -- Optimistic Locking
);
