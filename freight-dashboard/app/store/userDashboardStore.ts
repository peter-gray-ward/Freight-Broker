import { create } from "zustand";

type DashboardState = {
  shipments: any[];
  orders: any[];
  setShipments: (data: any[]) => void;
  setOrders: (data: any[]) => void;
};

export const useDashboardStore = create<DashboardState>((set) => ({
  shipments: [],
  orders: [],
  setShipments: (data) => set({ shipments: data }),
  setOrders: (data) => set({ orders: data }),
}));
