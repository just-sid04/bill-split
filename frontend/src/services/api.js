const BASE_URL = "http://localhost:5000/api/v1";

export async function fetchBalances(groupId) {
  const response = await fetch(`${BASE_URL}/groups/${groupId}/balances`);
  if (!response.ok) throw new Error("Failed to fetch balances");
  return response.json();
}

export async function createExpense(expenseData) {
  const response = await fetch(`${BASE_URL}/expenses`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(expenseData)
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || "Failed to create expense");
  }

  return response.json();
}

export async function createSettlement(settlementData) {
  const response = await fetch(`${BASE_URL}/settlements`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(settlementData)
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || "Failed to record settlement");
  }

  return response.json();
}

export async function confirmSettlement(settlementId) {
  const response = await fetch(
    `${BASE_URL}/settlements/${settlementId}/confirm`,
    { method: "POST" }
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || "Failed to confirm settlement");
  }

  return response.json();
}

export async function completeSettlement(settlementId) {
  const response = await fetch(
    `${BASE_URL}/settlements/${settlementId}/complete`,
    { method: "POST" }
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || "Failed to complete settlement");
  }

  return response.json();
}