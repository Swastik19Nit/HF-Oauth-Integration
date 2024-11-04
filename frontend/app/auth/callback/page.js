"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function Callback() {
  const router = useRouter();
  
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get("code");
    
    fetch(`/api/v1/auth/callback?code=${code}`)
      .then((res) => res.json())
      .then((data) => {
        localStorage.setItem("token", data.token);
        router.push("/");
      });
  }, [router]);
  
  return <div>Finishing up...</div>;
}
