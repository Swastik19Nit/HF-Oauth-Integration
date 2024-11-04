"use client"
import axios from 'axios';

const Login = () => {
    const handleLogin = async () => {
        const response = await axios.get(`${process.env.NEXT_PUBLIC_API_URL}/login`);
        window.location.href = response.data.auth_url;
    };

    return (
        <button onClick={handleLogin}>Login with Hugging Face</button>
    );
};

export default Login;
