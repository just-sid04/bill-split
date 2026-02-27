import React from "react";

function DebtList({ debts }) {
  return (
    <div>
      <h2 style={{ marginBottom: "15px" }}>Simplified Debts</h2>

      {debts.length === 0 ? (
        <p style={{ color: "#666" }}>No outstanding debts 🎉</p>
      ) : (
        debts.map((debt) => (
          <div
            key={`${debt.from_user_id}-${debt.to_user_id}`}
            style={{
              padding: "12px 16px",
              marginBottom: "10px",
              borderRadius: "8px",
              backgroundColor: "#fff3e0",
              color: "#ef6c00",
              fontWeight: "500"
            }}
          >
            {debt.from_user_name} pays {debt.to_user_name} {debt.amount}
          </div>
        ))
      )}
    </div>
  );
}

export default DebtList;