"use client";

import dynamic from "next/dynamic";
import { useLogin, useLoadActiveUsers, useShipments, useSchedules } from "./lib/api";

import { useWebSocket } from './lib/websocket';

const DataTable = dynamic(() => import("./lib/datatable"));
const FreighterMap = dynamic(() => import("./components/FreighterMap"));



export default function Dashboard() {
  const { data: user, isLoading, error } = useLogin();
  const { activeUsers, freighterUpdates, shipmentUpdates, sendMessage } = useWebSocket();
  const { data: activeUsersInitial } = useLoadActiveUsers();
  const { data: shipments } = useShipments()
  const { data: schedules } = useSchedules()

  if (isLoading) return <p>🔄 Logging in...</p>;
  if (error) return <p>❌ Failed to log in: {error.message}</p>;

  let au = activeUsers.length ? activeUsers : activeUsersInitial;
  au = au.length ? au.map(u => ({ name: u.name, role: u.role })) : []

  let su = shipmentUpdates.length ? shipmentUpdates : shipments;

  let fu = freighterUpdates.length ? freighterUpdates : (schedules || []);

  return (
    <main id="dashboard" className="p-6 w-full">
      <div id="top" className="h-3/5 w-full">
        <section id="language-stats" className="w-1/4 h-full">
          <h1 className="text-2xl font-bold">🚛 Freight Broker Dashboard</h1>
        </section>

        <section id="map" className="w-3/5 h-full">
          <FreighterMap freighters={fu} shipments={su} />
        </section>

        <section id="users" className="w-1/5 h-full">
          <h2 className="text-xl font-semibold mt-4">😊 Active Users</h2>
          {DataTable(au)}
        </section>
      </div>

      <div id="bottom" className="h-2/5 w-full">
        <section id="schedules" className="h-full w-1/2">
          <h2 className="w-1/2 text-xl font-semibold mt-4">🕒 Schedules ({fu ? fu.length : 0})</h2>
          {DataTable(fu)}
        </section>
        <section id="shipments" className="h-full w-1/2">
          <h2 className="w-1/2 text-xl font-semibold mt-4">📦 Shipments ({su ? su.length : 0})</h2>
          {DataTable(su)}
        </section>
      </div>
    </main>
  );
}
