"use client";
import React, { useEffect, useState } from 'react';
import axios from 'axios';

const Repositories = () => {
    const [repos, setRepos] = useState([]);

    useEffect(() => {
        const fetchRepos = async () => {
            try {
                const response = await axios.get(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/v1/repositories`, {
                    withCredentials: true
                });
                setRepos(response.data);
            } catch (error) {
                console.error("Error fetching repositories", error);
            }
        };
        fetchRepos();
    }, []);

    return (
        <div>
            <h1>Your Repositories</h1>
            <ul>
                {repos.map(repo => (
                    <li key={repo.id}>{repo.name}</li>
                ))}
            </ul>
        </div>
    );
};

export default Repositories;
