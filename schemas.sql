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

CREATE TABLE IF NOT EXISTS FreighterSchedules (
    ScheduleID     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    FreighterID    UUID REFERENCES Users(UserID) ON DELETE CASCADE,
    DepartureCity  VARCHAR(255),
    DepartureLat   DECIMAL(9,6),  -- Latitude with 6 decimal places
    DepartureLng   DECIMAL(9,6),  -- Longitude with 6 decimal places
    ArrivalCity    VARCHAR(255),
    ArrivalLat     DECIMAL(9,6),  -- Latitude with 6 decimal places
    ArrivalLng     DECIMAL(9,6),  -- Longitude with 6 decimal places
    DepartureDate  TIMESTAMP,
    ArrivalDate    TIMESTAMP,
    MaxLoadKg      DECIMAL(10,2),
    AvailableKg    DECIMAL(10,2),
    Status         VARCHAR(20) CHECK (Status IN ('Available', 'In Transit', 'Completed')),
    CreatedAt      TIMESTAMP DEFAULT NOW(),
    LastUpdated    TIMESTAMP DEFAULT NOW()  -- Optimistic Locking
);

CREATE TABLE IF NOT EXISTS ShipmentRequests (
    RequestID       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ClientID        UUID REFERENCES Users(UserID) ON DELETE CASCADE,
    OriginCity      VARCHAR(255),
    OriginLat       DECIMAL(9,6),  -- Latitude
    OriginLng       DECIMAL(9,6),  -- Longitude
    DestinationCity VARCHAR(255),
    DestinationLat  DECIMAL(9,6),  -- Latitude
    DestinationLng  DECIMAL(9,6),  -- Longitude
    WeightKg        DECIMAL(10,2),
    SpecialHandling VARCHAR(255),
    Status          VARCHAR(20) CHECK (Status IN ('Pending', 'Matched', 'Completed')),
    CreatedAt       TIMESTAMP DEFAULT NOW(),
    LastUpdated     TIMESTAMP DEFAULT NOW()  -- Optimistic Locking
);

CREATE TABLE IF NOT EXISTS ShipmentMatches (
    MatchID       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    RequestID     UUID REFERENCES ShipmentRequests(RequestID) ON DELETE CASCADE,
    ScheduleID    UUID REFERENCES FreighterSchedules(ScheduleID) ON DELETE CASCADE,
    MatchedAt     TIMESTAMP DEFAULT NOW(),
    Status        VARCHAR(20) CHECK (Status IN ('Pending', 'Confirmed', 'Rejected')),
    LastUpdated   TIMESTAMP DEFAULT NOW()  -- Optimistic Locking
);
