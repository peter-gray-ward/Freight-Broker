CREATE TABLE IF NOT EXISTS Users (
    UserID        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    Name          VARCHAR(255) NOT NULL,
    Email         VARCHAR(255) UNIQUE NOT NULL,
    PasswordHash  VARCHAR(255) NOT NULL,
    Role          VARCHAR(20) CHECK (Role IN ('Client', 'Freighter', 'Admin')),
    CreatedAt     TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS FreighterSchedules (
    ScheduleID     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    FreighterID    UUID REFERENCES Users(UserID) ON DELETE CASCADE,
    DepartureCity  VARCHAR(255) NOT NULL,
    DepartureLat   DECIMAL(9,6) NOT NULL,  -- Latitude with 6 decimal places
    DepartureLng   DECIMAL(9,6) NOT NULL,  -- Longitude with 6 decimal places
    ArrivalCity    VARCHAR(255) NOT NULL,
    ArrivalLat     DECIMAL(9,6) NOT NULL,  -- Latitude with 6 decimal places
    ArrivalLng     DECIMAL(9,6) NOT NULL,  -- Longitude with 6 decimal places
    DepartureDate  TIMESTAMP NOT NULL,
    ArrivalDate    TIMESTAMP NOT NULL,
    MaxLoadKg      DECIMAL(10,2) NOT NULL,
    AvailableKg    DECIMAL(10,2) NOT NULL,
    Status         VARCHAR(20) CHECK (Status IN ('Available', 'In Transit', 'Completed')),
    CreatedAt      TIMESTAMP DEFAULT NOW(),
    LastUpdated    TIMESTAMP DEFAULT NOW()  -- Optimistic Locking
);

CREATE TABLE IF NOT EXISTS ShipmentRequests (
    RequestID       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ClientID        UUID REFERENCES Users(UserID) ON DELETE CASCADE,
    OriginCity      VARCHAR(255) NOT NULL,
    OriginLat       DECIMAL(9,6) NOT NULL,  -- Latitude
    OriginLng       DECIMAL(9,6) NOT NULL,  -- Longitude
    DestinationCity VARCHAR(255) NOT NULL,
    DestinationLat  DECIMAL(9,6) NOT NULL,  -- Latitude
    DestinationLng  DECIMAL(9,6) NOT NULL,  -- Longitude
    WeightKg        DECIMAL(10,2) NOT NULL,
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
