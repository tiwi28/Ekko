import { useEffect, useState } from "react";
import { api } from "../api.js";

export default function TodoList() {
  const [tasks, setTasks] = useState([]);
  const [title, setTitle] = useState("");
  const [error, setError] = useState(null);

  useEffect(() => {
    api.tasks().then(setTasks).catch((e) => setError(e.message));
  }, []);

  const add = async (e) => {
    e.preventDefault();
    if (!title.trim()) return;
    // TODO: optimistic update / error handling
    const task = await api.createTask(title.trim()).catch((err) => setError(err.message));
    if (task) setTasks([task, ...tasks]);
    setTitle("");
  };

  // TODO: toggle complete (api.updateTask(id, { completed })), delete, show carried-over badge

  return (
    <section>
      <h2>Todo</h2>
      {error && <p className="muted">Couldn't load tasks: {error}</p>}
      <form onSubmit={add} className="row">
        <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Add a task" />
        <button type="submit">Add</button>
      </form>
      <ul className="tasks">
        {tasks.map((t) => (
          <li key={t.id} className={t.completed_at ? "done" : ""}>
            {t.title}
          </li>
        ))}
      </ul>
    </section>
  );
}
