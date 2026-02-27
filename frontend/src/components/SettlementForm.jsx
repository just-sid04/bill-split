import React, { useState } from "react";
import { createSettlement, confirmSettlement, completeSettlement } from "../services/api";

function SettlementForm({ users, onSettlementCreated }) {
  const [fromUser, setFromUser] = useState("");
  const [toUser, setToUser] = useState("");
  const [amount, setAmount] = useState("");
  const [notes, setNotes] = useState("");
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccess(false);

    if (fromUser === toUser) {
      setError("Cannot pay yourself");
      return;
    }

    try {
      const settlement = await createSettlement({
        from_user_id: parseInt(fromUser),
        to_user_id: parseInt(toUser),
        amount: parseFloat(amount).toFixed(2),
        notes: notes || `Payment from ${getUserName(fromUser)} to ${getUserName(toUser)}`
      });

      // Auto confirm + complete
      await confirmSettlement(settlement.id);
      await completeSettlement(settlement.id);

      setSuccess(true);
      setFromUser("");
      setToUser("");
      setAmount("");
      setNotes("");

      onSettlementCreated();

      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError(err.message);
    }
  };

  const getUserName = (id) => {
    const user = users.find(u => u.id === parseInt(id));
    return user ? user.name : "";
  };

  if (users.length === 0) return null;

  return (
    <div style={{ 
      marginBottom: "30px", 
      padding: "20px", 
      backgroundColor: "#e3f2fd",
      borderRadius: "8px"
    }}>
      <h3>💸 Record Payment</h3>
      <p style={{ color: "#666", fontSize: "0.9em", marginBottom: "15px" }}>
        Record when someone pays another person directly
      </p>

      {error && (
        <p style={{ color: "red", padding: "10px", background: "#ffebee", borderRadius: "4px" }}>
          {error}
        </p>
      )}

      {success && (
        <p style={{ color: "green", padding: "10px", background: "#e8f5e9", borderRadius: "4px" }}>
          ✓ Payment recorded!
        </p>
      )}

      <form onSubmit={handleSubmit}>
        <div style={{ display: "flex", gap: "10px", marginBottom: "15px" }}>
          <div style={{ flex: 1 }}>
            <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>
              From (Who paid)
            </label>
            <select
              value={fromUser}
              onChange={(e) => setFromUser(e.target.value)}
              required
              style={{ padding: "10px", width: "100%", borderRadius: "4px", border: "1px solid #ddd" }}
            >
              <option value="">Select...</option>
              {users.map(user => (
                <option key={user.id} value={user.id}>
                  {user.name}
                </option>
              ))}
            </select>
          </div>

          <div style={{ flex: 1 }}>
            <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>
              To (Who received)
            </label>
            <select
              value={toUser}
              onChange={(e) => setToUser(e.target.value)}
              required
              style={{ padding: "10px", width: "100%", borderRadius: "4px", border: "1px solid #ddd" }}
            >
              <option value="">Select...</option>
              {users.map(user => (
                <option key={user.id} value={user.id}>
                  {user.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div style={{ marginBottom: "15px" }}>
          <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>
            Amount ($)
          </label>
          <input
            type="number"
            step="0.01"
            min="0.01"
            placeholder="0.00"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            required
            style={{ padding: "10px", width: "200px", borderRadius: "4px", border: "1px solid #ddd" }}
          />
        </div>

        <div style={{ marginBottom: "15px" }}>
          <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>
            Notes (optional)
          </label>
          <input
            type="text"
            placeholder="e.g., Cash payment, Bank transfer"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            style={{ padding: "10px", width: "100%", borderRadius: "4px", border: "1px solid #ddd" }}
          />
        </div>

        <button
          type="submit"
          style={{
            padding: "12px 24px",
            backgroundColor: "#388e3c",
            color: "white",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer",
            fontSize: "16px",
            fontWeight: "bold"
          }}
        >
          Record Payment
        </button>
      </form>
    </div>
  );
}

export default SettlementForm;