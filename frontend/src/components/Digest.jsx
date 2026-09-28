import { useEffect, useState } from "react";
import { api } from "../api.js";

export default function Digest() {
  const [digest, setDigest] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.todayDigest().then(setDigest).catch((e) => setError(e.message));
  }, []);

  // TODO: record clicks with api.interact(item.id, "click"); add save/dismiss buttons

  return (
    <section>
      <h2>Today's digest</h2>
      {error && <p className="muted">Couldn't load digest: {error}</p>}
      {digest && (
        <ol className="digest">
          {digest.items.map((item) => (
            <li key={item.id}>
              <a href={item.url} target="_blank" rel="noreferrer">
                {item.title}
              </a>
              <span className="muted"> · {item.source}{item.topic && ` · ${item.topic.name}`}</span>
              <p>{item.summary}</p>
              <p className="why"><strong>Why it matters:</strong> {item.why_it_matters}</p>
            </li>
          ))}
        </ol>
      )}
    </section>
  );
}
