import React from "react";

function BalanceList({ balances }) {
  return (
    <div style={{ marginBottom: "40px" }}>
      <h2 style={{ marginBottom: "15px" }}>Member Balances</h2>

      {balances.map((member) => {
        const isPositive = parseFloat(member.net_balance) >= 0;

        return (
          <div
            key={member.user_id}
            style={{
              display: "flex",
              justifyContent: "space-between",
              padding: "12px 16px",
              marginBottom: "10px",
              borderRadius: "8px",
              backgroundColor: isPositive ? "#e6f4ea" : "#fdecea",
              color: isPositive ? "#1e7e34" : "#c62828",
              fontWeight: "600"
            }}
          >
            <span>{member.user_name}</span>
            <span>{member.net_balance}</span>
          </div>
        );
      })}
    </div>
  );
}

export default BalanceList;