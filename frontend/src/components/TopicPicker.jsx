import { useEffect, useState } from "react";
import { api } from "../api.js";

export default function TopicPicker() {
  const [topics, setTopics] = useState([]);
  const [selected, setSelected] = useState(new Set());
  const [error, setError] = useState(null);

  useEffect(() => {
    api.topics().then(setTopics).catch((e) => setError(e.message));
    // TODO: load the user's selection with api.myTopics() once logged in
  }, []);

  const toggle = (slug) => {
    const next = new Set(selected);
    next.has(slug) ? next.delete(slug) : next.add(slug);
    setSelected(next);
    // TODO: persist with api.setMyTopics([...next])
  };

  return (
    <section>
      <h2>Topics</h2>
      {error && <p className="error">{error}</p>}
      <div className="chips">
        {topics.map((t) => (
          <button
            key={t.slug}
            className={selected.has(t.slug) ? "chip on" : "chip"}
            onClick={() => toggle(t.slug)}
          >
            {t.name}
          </button>
        ))}
      </div>
    </section>
  );
}
