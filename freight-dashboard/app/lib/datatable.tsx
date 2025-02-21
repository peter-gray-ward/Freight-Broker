"use client";

import { useEffect, useState } from "react";

export default function DataTable(objects) {
  if (!objects) return null
  if (!Array.isArray(objects)) {
  	objects = Object.values(objects);
  }
  if (!objects.length) return null
  var keys = Object.keys(objects[0])
  return (
    <div className="datatable overflow-x-auto">
      <table className="min-w-full border border-gray-300 shadow-md rounded-lg">
        {/* Table Header */}
        <thead>
          <tr>
            {
              keys.map((key, i) => <th key={i} className="border text-left">{key}</th>)
            }
          </tr>
        </thead>

        {/* Table Body */}
        <tbody className="divide-y divide-gray-300">
          {
            objects.map((obj, i) => <tr key={i}>
              {
                keys.map((key, j) => <td key={j} className="border">{obj[key]}</td>)
              }
            </tr>)
          }
        </tbody>
      </table>
    </div>
  );
}