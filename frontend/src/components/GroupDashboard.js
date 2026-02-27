import React, { useEffect, useState } from "react";
import { fetchBalances } from "../services/api";
import BalanceList from "./BalanceList";
import DebtList from "./DebtList";
import ExpenseForm from "./ExpenseForm";
import SettlementForm from "./SettlementForm";

function GroupDashboard() {
  const [balances, setBalances] = useState([]);
  const [debts, setDebts] = useState([]);
  const [users, setUsers] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      const data = await fetchBalances(1);
      setBalances(data.balances);
      setDebts(data.simplified_debts);
      setUsers(data.balances.map(b => ({ id: b.user_id, name: b.user_name })));
    } catch (err) {
      setError(err.message);
    }
  }

  if (error) return <p style={{ color: "red" }}>{error}</p>;

  return (
    <div>
      <h1>💰 Group 1 Dashboard</h1>
      <button 
        onClick={loadData} 
        style={{ 
          marginBottom: "20px",
          padding: "8px 16px",
          background: "#1976d2",
          color: "white",
          border: "none",
          borderRadius: "4px",
          cursor: "pointer"
        }}
      >
        🔄 Refresh
      </button>
      
      <ExpenseForm 
        groupId={1} 
        users={users} 
        onExpenseCreated={loadData} 
      />
      
      <SettlementForm 
        users={users} 
        onSettlementCreated={loadData} 
      />
      
      <BalanceList balances={balances} />
      <DebtList debts={debts} />
    </div>
  );
}

export default GroupDashboard;