"use client";
import { useState, useEffect } from "react";

export default function HomePage() {
  const [repositories, setRepositories] = useState([]);
  
  useEffect(() => {
    const token = localStorage.getItem("token");
    fetch("/api/v1/repositories", {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => res.json())
      .then((data) => setRepositories(data));
  }, []);
  
  return (
    <div>
      <h1>Repositories</h1>
      <ul>
        {repositories.map((repo) => (
          <li key={repo.id}>{repo.name}</li>
        ))}
      </ul>
    </div>
  );
}
