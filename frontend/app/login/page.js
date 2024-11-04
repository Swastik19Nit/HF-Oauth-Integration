"use client";

import { useState } from "react";
import Router from "next/router";
import axios from "axios";

const Login = () => {
  const [hfToken, setHfToken] = useState("");

  const handleLogin = async () => {
    try {
      const response = await axios.post(`${NEXT_PUBLIC_API_URL}/login`, { hf_access_token: hfToken });

      if (response.status === 200) {
        
        localStorage.setItem("token", response.data.token);
        Router.push("/repositories"); 
      }
    } catch (error) {
      console.error("Login failed:", error);
      alert("Login failed. Please check your Hugging Face access token.");
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-white text-black">
      <h1 className="text-2xl font-bold mb-6">Login with Hugging Face</h1>
      <input
        type="text"
        placeholder="Enter your Hugging Face access token"
        value={hfToken}
        onChange={(e) => setHfToken(e.target.value)}
        required
        className="w-80 p-3 mb-4 border border-black rounded focus:outline-none focus:ring focus:ring-gray-500"
      />
      <button
        onClick={handleLogin}
        className="w-80 p-3 bg-black text-white rounded hover:bg-gray-800 transition-colors"
      >
        Login
      </button>
    </div>
  );
};

export default Login;
