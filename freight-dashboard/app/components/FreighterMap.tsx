"use client";

import { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";

import L from 'leaflet';

const icon = (which) => L.icon({
  iconUrl: which + '-marker.png',
  iconSize: which == 'freighter' ? [1280 / 50,708 / 50] : [1280 / 50, 1271 / 50],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});


const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function FreighterMap(props) {
  return (
    <MapContainer center={[39.5, -98.35]} zoom={4} className="h-full w-full rounded-lg">
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        {props.freighters.map((freighter, i) => (
          <Marker key={i} position={[freighter.departurelat, freighter.departurelng]} icon={icon('freighter')}>
            <Popup>
              <strong>{freighter.freighterid}</strong> <br />
              Status: {freighter.status} <br />
              Load: {freighter.availablekg} / {freighter.maxloadkg} kg
            </Popup>
          </Marker>
        ))}
        {props.shipments.map((shipment, i) => (
          <Marker key={i} position={[shipment.originlat, shipment.originlng]} icon={icon('shipment')}>
            <Popup>
              <strong>{shipment.requestid}</strong> <br />
              Status: {shipment.status} <br />
              Load: {shipment.weightkg} kg
            </Popup>
          </Marker>
        ))}
    </MapContainer>
  );
}
