import { useQuery } from "@tanstack/react-query";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const headers = {
  "Content-Type": "application/json"
};

export function useLogin() {
  return useQuery({
    queryKey: ["login"],
    queryFn: async () => {
      const res = await fetch(`${API_URL}/users/login`, {
        method: "POST",
        headers,
        body: JSON.stringify({
          name: "Peter",
          password: "enter"
        }),
        credentials: "include"
      });

      if (!res.ok) throw new Error("Login failed");

      return res.json();
    },
    retry: false
  })
}

export function useLoadActiveUsers() {
  return useQuery({
    queryKey: ["load-active-users"],
    queryFn: async () => {
      const res = await fetch(`${API_URL}/active-users`, {
        method: "GET",
        headers,
        credentials: "include"
      });

      if (!res.ok) throw new Error("Load Active Users failed");

      return res.json();
    }
  })
}

export function useShipments() {
  return useQuery({
    queryKey: ["shipments"],
    queryFn: async () => {
      const res = await fetch(`${API_URL}/shipments/requests`);
      return res.json();
    },
    refetchInterval: 5000, // Poll every 5 seconds
  });
}

export function useOrders() {
  return useQuery({
    queryKey: ["orders"],
    queryFn: async () => {
      const res = await fetch(`${API_URL}/orders`);
      return res.json();
    },
    refetchInterval: 5000,
  });
}
