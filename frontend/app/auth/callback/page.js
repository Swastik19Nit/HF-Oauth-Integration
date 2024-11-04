"use client"
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

const Callback = () => {
  const router = useRouter();
  const query = new URLSearchParams(window.location.search);
  const code = query.get('code');

  useEffect(() => {
    if (code) {
      (async () => {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/auth/callback?code=${code}`
        );
        if (response.ok) {
          router.push('/'); 
        } else {
          alert('Authentication failed');
        }
      })();
    }
  }, [code, router]);

  return <p>Completing authentication...</p>;
};

export default Callback;
