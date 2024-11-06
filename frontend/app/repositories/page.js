"use client"
import React, { useEffect, useState } from 'react';
import axios from 'axios';

const Repositories = () => {
    const [repos, setRepos] = useState([]);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchRepos = async () => {
            const baseUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
            const endpoint = `${baseUrl}/api/v1/endpoints/repositories/get`;

            console.log('Attempting to fetch from:', endpoint);
            const token = localStorage.getItem('token'); 
            console.log(token);

            try {
                setLoading(true);
                const response = await axios.get(endpoint, {
                    withCredentials: true,
                    headers: {
                        'Content-Type': 'application/json',
                        
                    }
                });

                console.log('Response received:', response,"Hi");
                setRepos(response.data);
                setError(null);
            } catch (err) {
                console.error('Detailed error:', {
                    message: err.message,
                    response: err.response,
                    status: err.response?.status,
                    data: err.response?.data
                });

                if (err.response?.status === 404) {
                    setError("API endpoint not found. Please check the server configuration.");
                } else if (err.response?.status === 401) {
                    setError("Please log in to view your repositories");
                } else {
                    setError(`Failed to fetch repositories: ${err.message}`);
                }
            } finally {
                setLoading(false);
            }
        };

        fetchRepos();
    }, []);

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-[200px]">
                <div className="text-lg">Loading repositories...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="max-w-2xl mx-auto mt-8 p-4 bg-red-50 text-red-500 rounded-lg">
                <p className="font-bold">Error:</p>
                <p>{error}</p>
            </div>
        );
    }

    return (
        <div className="max-w-2xl mx-auto mt-8">
            <h1 className="text-2xl font-bold mb-6">Your Repositories</h1>
            {repos.length === 0 ? (
                <div className="text-gray-500">No repositories found</div>
            ) : (
                <ul className="space-y-4">
                    {repos.map((repo) => (
                        <li
                            key={repo.id}
                            className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50"
                        >
                            <div className="font-medium">{repo.name}</div>
                            {repo.description && (
                                <div className="text-sm text-gray-500">{repo.description}</div>
                            )}
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
};

export default Repositories;