"use client"
import { useEffect } from 'react';

const Login = () => {
  useEffect(() => {
    window.location.href = `${process.env.NEXT_PUBLIC_API_URL}/auth/login`;
  }, []);

  return <p>Redirecting to Hugging Face for authentication...</p>;
};

export default Login;
