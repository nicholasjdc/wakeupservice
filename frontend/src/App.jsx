import { useState } from "react";
import "./App.css";

function App() {
  const [form, setForm] = useState({
    name: "",
    phone: "",
    call_time: "",
    max_attempts: "",
    notes: "",
  });
  const [submitted, setSubmitted] = useState(false);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch("/api/submit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      if (res.ok) {
        setSubmitted(true);
      }
    } catch (err) {
      alert("Error submitting form");
    }
  };

  if (submitted) {
    return (
      <div className="container thank-you">
        <p>Thank you. We will get back to you soon regarding your request.</p>
      </div>
    );
  }

  return (
    <div className="container">
      <h1>Survey</h1>
      <form onSubmit={handleSubmit}>
        <label>
          Name
          <input name="name" value={form.name} onChange={handleChange} />
        </label>
        <label>
          Phone Number
          <input name="phone" value={form.phone} onChange={handleChange} />
        </label>
        <label>
          When would you like us to call you?
          <input name="call_time" value={form.call_time} onChange={handleChange} />
        </label>
        <label>
          How many times should we call before giving up?
          <input name="max_attempts" value={form.max_attempts} onChange={handleChange} />
        </label>
        <label>
          Anything else we should know?
          <input name="notes" value={form.notes} onChange={handleChange} />
        </label>
        <button type="submit">Submit</button>
      </form>
    </div>
  );
}

export default App;
