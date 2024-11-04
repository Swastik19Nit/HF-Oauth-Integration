"use client";

import { useState, useEffect } from "react";

const API_URL = "http://localhost:8000/api/v1";

export default function RepositoriesPage() {
  const [token, setToken] = useState(null);
  const [repositories, setRepositories] = useState([]);
  const [repoName, setRepoName] = useState("");
  const [repoDescription, setRepoDescription] = useState("");
  const [repoPrivate, setRepoPrivate] = useState(false);

  useEffect(() => {
    const savedToken = localStorage.getItem("token");
    if (savedToken) {
      setToken(savedToken);
      fetchRepositories(savedToken);
    } else {
      window.location.href = "/login";
    }
  }, []);

  const fetchRepositories = async (authToken) => {
    const response = await fetch(`${API_URL}/repositories`, {
      headers: {
        Authorization: `Bearer ${authToken}`,
      },
    });
    const data = await response.json();
    setRepositories(data);
  };

  const createRepository = async () => {
    if (!repoName) return;
    const response = await fetch(`${API_URL}/repositories`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        name: repoName,
        description: repoDescription,
        private: repoPrivate,
      }),
    });

    if (response.ok) {
      const newRepo = await response.json();
      setRepositories((prev) => [...prev, newRepo]);
      setRepoName("");
      setRepoDescription("");
      setRepoPrivate(false);
    }
  };

  const deleteRepository = async (repoId) => {
    const response = await fetch(`${API_URL}/repositories/${repoId}`, {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (response.ok) {
      setRepositories((prev) => prev.filter((repo) => repo.id !== repoId));
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token"); // Clear the stored token
    window.location.href = "/"; // Redirect to home page
  };

  return (
    <div>
      <h1>Your Hugging Face Repositories</h1>
      <h2>Create Repository</h2>
      <input
        type="text"
        placeholder="Repository Name"
        value={repoName}
        onChange={(e) => setRepoName(e.target.value)}
      />
      <textarea
        placeholder="Description"
        value={repoDescription}
        onChange={(e) => setRepoDescription(e.target.value)}
      />
      <label>
        Private:
        <input
          type="checkbox"
          checked={repoPrivate}
          onChange={(e) => setRepoPrivate(e.target.checked)}
        />
      </label>
      <button onClick={createRepository}>Create Repository</button>
      <button onClick={handleLogout}>Logout</button>

      <h2>Your Repositories</h2>
      <ul>
        {repositories.map((repo) => (
          <li key={repo.id}>
            {repo.name} <button onClick={() => deleteRepository(repo.id)}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
}
