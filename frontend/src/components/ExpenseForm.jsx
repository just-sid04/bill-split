import React, { useState, useEffect } from "react";
import { createExpense } from "../services/api";

function ExpenseForm({ groupId, users, onExpenseCreated }) {
  const [description, setDescription] = useState("");
  const [amount, setAmount] = useState("");
  const [paidBy, setPaidBy] = useState("");
  const [splitType, setSplitType] = useState("equal"); // equal, custom
  const [customSplits, setCustomSplits] = useState({});
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  // Calculate equal splits automatically
  const calculateEqualSplits = () => {
    if (!amount || users.length === 0) return {};
    
    const total = parseFloat(amount);
    const perPerson = (total / users.length).toFixed(2);
    
    const splits = {};
    users.forEach(user => {
      splits[user.id] = perPerson;
    });
    
    return splits;
  };

  // Update splits when amount or splitType changes
  useEffect(() => {
    if (splitType === "equal") {
      setCustomSplits(calculateEqualSplits());
    }
  }, [amount, splitType, users]);

  const handleCustomSplitChange = (userId, value) => {
    setCustomSplits({ ...customSplits, [userId]: value });
  };

  const getSplitsArray = () => {
    return Object.entries(customSplits)
      .filter(([_, amount]) => amount !== "" && parseFloat(amount) > 0)
      .map(([userId, amount]) => ({
        user_id: parseInt(userId),
        amount: parseFloat(amount).toFixed(2)
      }));
  };

  const validateSplits = () => {
    const splits = getSplitsArray();
    const total = splits.reduce((sum, s) => sum + parseFloat(s.amount), 0);
    const expected = parseFloat(amount);
    return Math.abs(total - expected) < 0.01; // Allow 1 cent rounding error
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccess(false);

    if (!validateSplits()) {
      setError(`Splits must equal total amount: $${amount}`);
      return;
    }

    const splitsArray = getSplitsArray();

    try {
      await createExpense({
        group_id: groupId,
        paid_by: parseInt(paidBy),
        description,
        amount: parseFloat(amount).toFixed(2),
        splits: splitsArray
      });

      setSuccess(true);
      setDescription("");
      setAmount("");
      setPaidBy("");
      setSplitType("equal");
      setCustomSplits({});
      onExpenseCreated();
      
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError(err.message);
    }
  };

  if (users.length === 0) return <p>Loading users...</p>;

  return (
    <div style={{ 
      marginBottom: "30px", 
      padding: "20px", 
      backgroundColor: "#f5f5f5",
      borderRadius: "8px"
    }}>
      <h3>💰 Add New Expense</h3>
      
      {error && <p style={{ color: "red", padding: "10px", background: "#ffebee", borderRadius: "4px" }}>{error}</p>}
      {success && <p style={{ color: "green", padding: "10px", background: "#e8f5e9", borderRadius: "4px" }}>✓ Expense added successfully!</p>}

      <form onSubmit={handleSubmit}>
        {/* Description */}
        <div style={{ marginBottom: "15px" }}>
          <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>
            What was this for?
          </label>
          <input
            type="text"
            placeholder="e.g., Dinner, Groceries, Taxi"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            required
            style={{ padding: "10px", width: "100%", borderRadius: "4px", border: "1px solid #ddd" }}
          />
        </div>

        {/* Total Amount */}
        <div style={{ marginBottom: "15px" }}>
          <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>
            Total Amount ($)
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

        {/* Who Paid */}
        <div style={{ marginBottom: "15px" }}>
          <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>
            Who paid?
          </label>
          <select
            value={paidBy}
            onChange={(e) => setPaidBy(e.target.value)}
            required
            style={{ padding: "10px", width: "100%", borderRadius: "4px", border: "1px solid #ddd" }}
          >
            <option value="">Select person...</option>
            {users.map((user) => (
              <option key={user.id} value={user.id}>
                {user.name}
              </option>
            ))}
          </select>
        </div>

        {/* Split Type */}
        <div style={{ marginBottom: "15px" }}>
          <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>
            How to split?
          </label>
          <div>
            <label style={{ marginRight: "20px" }}>
              <input
                type="radio"
                value="equal"
                checked={splitType === "equal"}
                onChange={(e) => setSplitType(e.target.value)}
              /> Equal split
            </label>
            <label>
              <input
                type="radio"
                value="custom"
                checked={splitType === "custom"}
                onChange={(e) => setSplitType(e.target.value)}
              /> Custom amounts
            </label>
          </div>
        </div>

        {/* Split Details */}
        <div style={{ marginBottom: "20px", padding: "15px", background: "white", borderRadius: "4px" }}>
          <p style={{ marginBottom: "10px", fontWeight: "bold" }}>Split details:</p>
          {users.map((user) => (
            <div key={user.id} style={{ 
              display: "flex", 
              justifyContent: "space-between", 
              alignItems: "center",
              padding: "8px 0",
              borderBottom: "1px solid #eee"
            }}>
              <span>{user.name} {parseInt(paidBy) === user.id && "💳 (paid)"}</span>
              
              {splitType === "equal" ? (
                <span style={{ fontWeight: "bold", color: "#1976d2" }}>
                  ${customSplits[user.id] || "0.00"}
                </span>
              ) : (
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  value={customSplits[user.id] || ""}
                  onChange={(e) => handleCustomSplitChange(user.id, e.target.value)}
                  style={{ padding: "5px", width: "100px", borderRadius: "4px", border: "1px solid #ddd" }}
                />
              )}
            </div>
          ))}
          
          {splitType === "custom" && (
            <p style={{ marginTop: "10px", fontSize: "0.9em", color: "#666" }}>
              Total: ${getSplitsArray().reduce((sum, s) => sum + parseFloat(s.amount), 0).toFixed(2)} / ${amount || "0.00"}
            </p>
          )}
        </div>

        <button
          type="submit"
          style={{
            padding: "12px 24px",
            backgroundColor: "#1976d2",
            color: "white",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer",
            fontSize: "16px",
            fontWeight: "bold"
          }}
        >
          Add Expense
        </button>
      </form>
    </div>
  );
}

export default ExpenseForm;