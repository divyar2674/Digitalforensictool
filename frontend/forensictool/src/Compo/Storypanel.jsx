import { useLocation } from "react-router-dom";

function Storypanel() {
  const location = useLocation();
  const story = location.state?.story;
  console.log("Received story:", story);

  return (
    <div>
      <h2>🧠 Story</h2>
      <div style={{ whiteSpace: "pre-line" }}>
        {story || "No data"}
      </div>
    </div>
  );
}
export default Storypanel;