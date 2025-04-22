'use client';

import { useEffect, useState } from 'react';

export interface User {
  name?: string;
  preferred_username?: string;
  email?: string;
  [key: string]: any;
}

export function useUser() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const res = await fetch('http://localhost:8000/me', {
          credentials: 'include',
        });

        if (res.status === 401) {
          // 🚨 Hard redirect immediately when not logged in
          window.location.href = 'http://localhost:8000/login';
          return;
        }

        const data = await res.json();
        setUser(data);
      } catch (error) {
        console.error('Error fetching user:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, []);

  return { user, loading };
}
