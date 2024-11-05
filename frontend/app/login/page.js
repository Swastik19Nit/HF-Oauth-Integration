"use client";
import React from 'react';

const Login = () => {
    const handleLogin = () => {
        window.location.href = `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/v1/auth/login`;
    };

    return (
        <div className="flex flex-col items-center justify-center min-h-screen text-center">
            <h1 className="text-4xl font-bold mb-8">Sign Up / Log In</h1>
            <div 
                className="p-4 border-2 border-gray-300 rounded-lg cursor-pointer hover:border-gray-500"
                onClick={handleLogin}
            >
                <img 
                    src="https://huggingface.co/datasets/huggingface/badges/resolve/main/sign-in-with-huggingface-xl-dark.svg" 
                    alt="Sign in with Hugging Face"
                    className="w-72"
                />
            </div>
        </div>
    );
};

export default Login;
