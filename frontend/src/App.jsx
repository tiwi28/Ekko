import { useEffect, useState } from "react";
import { api } from "./api.js";
import TopicPicker from "./components/TopicPicker.jsx";
import Digest from "./components/Digest.jsx";
import TodoList from "./components/TodoList.jsx";

export default function App() {
  const [apiStatus, setApiStatus] = useState("checking…");

  useEffect(() => {
    api
      .health()
      .then((r) => setApiStatus(r.status))
      .catch(() => setApiStatus("unreachable"));
  }, []);

  // TODO: auth. Show a login/signup form when there's no token (getToken() from api.js),
  // call api.login / api.signup, store the token with setToken.

  return (
    <main className="container">
      <header>
        <h1>Ekko</h1>
        <small>API: {apiStatus}</small>
      </header>
      <TopicPicker />
      <Digest />
      <TodoList />
    </main>
  );
}
