"use client";

import { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function FreighterMap() {
  const [freighters, setFreighters] = useState([]);

  return (
    <MapContainer center={[39.5, -98.35]} zoom={4} className="h-full w-full rounded-lg">
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      {freighters.map((freighter) => (
        <Marker key={freighter.id} position={[freighter.lat, freighter.lng]}>
          <Popup>
            <strong>{freighter.name}</strong> <br />
            Status: {freighter.status} <br />
            Load: {freighter.availableKg} / {freighter.maxLoadKg} kg
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}
