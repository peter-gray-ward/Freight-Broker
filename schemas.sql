CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE Users (
    UserID         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    Name          VARCHAR(255) NOT NULL,
    Email         VARCHAR(255) UNIQUE NOT NULL,
    PasswordHash  VARCHAR(255) NOT NULL,
    Role          VARCHAR(20) CHECK (Role IN ('Client', 'Freighter', 'Admin')),
    CreatedAt     TIMESTAMP DEFAULT NOW()
);


CREATE TABLE FreighterSchedules (
    ScheduleID     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    FreighterID    UUID REFERENCES Users(UserID) ON DELETE CASCADE,
    DepartureCity  VARCHAR(255) NOT NULL,
    DepartureLocation GEOGRAPHY(POINT, 4326) NOT NULL,  -- Stores lat/lon as a geospatial point
    ArrivalCity    VARCHAR(255) NOT NULL,
    ArrivalLocation GEOGRAPHY(POINT, 4326) NOT NULL,
    DepartureDate  TIMESTAMP NOT NULL,
    ArrivalDate    TIMESTAMP NOT NULL,
    MaxLoadKg      DECIMAL(10,2) NOT NULL,
    AvailableKg    DECIMAL(10,2) NOT NULL,
    Status         VARCHAR(20) CHECK (Status IN ('Available', 'In Transit', 'Completed')),
    CreatedAt      TIMESTAMP DEFAULT NOW(),
    LastUpdated    TIMESTAMP DEFAULT NOW()  -- Optimistic Locking
);


CREATE TABLE ShipmentRequests (
    RequestID       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ClientID        UUID REFERENCES Users(UserID) ON DELETE CASCADE,
    OriginCity      VARCHAR(255) NOT NULL,
    OriginLocation  GEOGRAPHY(POINT, 4326) NOT NULL,  -- Lat/lon stored as geospatial point
    DestinationCity VARCHAR(255) NOT NULL,
    DestinationLocation GEOGRAPHY(POINT, 4326) NOT NULL,
    WeightKg        DECIMAL(10,2) NOT NULL,
    SpecialHandling VARCHAR(255),
    Status          VARCHAR(20) CHECK (Status IN ('Pending', 'Matched', 'Completed')),
    CreatedAt       TIMESTAMP DEFAULT NOW(),
    LastUpdated     TIMESTAMP DEFAULT NOW()  -- Optimistic Locking
);

CREATE TABLE ShipmentMatches (
    MatchID       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    RequestID     UUID REFERENCES ShipmentRequests(RequestID) ON DELETE CASCADE,
    ScheduleID    UUID REFERENCES FreighterSchedules(ScheduleID) ON DELETE CASCADE,
    MatchedAt     TIMESTAMP DEFAULT NOW(),
    Status        VARCHAR(20) CHECK (Status IN ('Pending', 'Confirmed', 'Rejected')),
    LastUpdated   TIMESTAMP DEFAULT NOW()  -- Optimistic Locking
);

