import { createRoot } from "react-dom/client";
import App from "./App";
import "./index.css";
import "leaflet/dist/leaflet.css";

const root = document.getElementById("root");

if (!root) {
  throw new Error("Root container missing in index.html");
}

createRoot(root).render(<App />);
