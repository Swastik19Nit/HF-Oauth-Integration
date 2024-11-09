"use client"
import React, { useEffect, useState } from 'react';
import axios from 'axios';

const Repositories = () => {
    const [repos, setRepos] = useState([]);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(true);
    const [deleteLoading, setDeleteLoading] = useState(null);

    const baseUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

    const fetchRepos = async () => {
        const endpoint = `${baseUrl}/api/v1/endpoints/repositories/get`;
        
        try {
            setLoading(true);
            const response = await axios.get(endpoint, {
                withCredentials: true,
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            setRepos(response.data);
            setError(null);
        } catch (err) {
            console.error('Error fetching repositories:', err);
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

    const handleDelete = async (name, organization) => {
        if (!window.confirm(`Are you sure you want to delete repository ${name}?`)) {
            return;
        }

        setDeleteLoading(name);
        try {
            await axios.delete(
                `${baseUrl}/api/v1/endpoints/repositories/delete`,
                {
                    data: {
                        type: "model",
                        name: name,
                        organization: organization
                    },
                    withCredentials: true,
                    headers: {
                        'Content-Type': 'application/json',
                    }
                }
            );

            // Refresh the repositories list
            await fetchRepos();
        } catch (err) {
            console.error('Error deleting repository:', err);
            setError(`Failed to delete repository: ${err.response?.data?.detail || err.message}`);
        } finally {
            setDeleteLoading(null);
        }
    };

    useEffect(() => {
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
                            className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 flex justify-between items-center"
                        >
                            <div>
                                <div className="font-medium">{repo.id}</div>
                                {repo.description && (
                                    <div className="text-sm text-gray-500">{repo.description}</div>
                                )}
                            </div>
                            <button
                                onClick={() => handleDelete(repo.id, repo.organization)}
                                disabled={deleteLoading === repo.id}
                                className={`px-4 py-2 rounded-md text-white text-sm
                                    ${deleteLoading === repo.id
                                        ? 'bg-gray-400'
                                        : 'bg-red-600 hover:bg-red-700'
                                    }`}
                            >
                                {deleteLoading === repo.id ? 'Deleting...' : 'Delete'}
                            </button>
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
};

export default Repositories;