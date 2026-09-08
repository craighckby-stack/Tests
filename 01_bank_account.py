"""Bank account management with statements and persistence."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, List, Literal, Sequence, Tuple, Union

TRANSACTIONS_FILE: str = "transactions.json"


class BankAccount:
    """A sovereign bank account supporting deposits, withdrawals, interest, and statements."""

    __slots__ = ("owner", "balance", "transactions")

    owner: str
    balance: float
    transactions: List[Dict[str, Any]]

    def __init__(
        self,
        owner: str,
        balance: float = 0.0,
        transactions: List[Dict[str, Any]] | None = None,
    ) -> None:
        """Initialize a bank account with owner, initial balance, and transaction history."""
        self.owner = owner
        self.balance = float(balance)
        self.transactions = list(transactions) if transactions is not None else []

    def deposit(self, amount: float) -> float:
        """Deposit funds into the account."""
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self.balance += float(amount)
        self.transactions.append(
            {"type": "deposit", "amount": float(amount), "timestamp": datetime.now()}
        )
        return self.balance

    # Alias preserved for backwards compatibility with legacy typo
    def depsoit(self, amount: float) -> float:
        """Deposit funds into the account (legacy alias)."""
        return self.deposit(amount)

    def withdraw(self, amount: float) -> float:
        """Withdraw funds from the account."""
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        self.balance -= float(amount)
        self.transactions.append(
            {"type": "withdrawal", "amount": float(amount), "timestamp": datetime.now()}
        )
        return self.balance

    def apply_interest(self, rate_percent: float) -> float:
        """Apply monthly interest to the balance."""
        self.balance += self.balance * float(rate_percent) / 100.0
        return self.balance

    def get_statement(self) -> str:
        """Return a formatted statement of every transaction."""
        lines = [f"Statement for {self.owner}"]
        for t in self.transactions:
            ts = t["timestamp"]
            if isinstance(ts, str):
                try:
                    ts_dt = datetime.fromisoformat(ts)
                except ValueError:
                    ts_dt = datetime.now()
            else:
                ts_dt = ts
            lines.append(
                f"{ts_dt:%Y-%m-%d %H:%M}  {str(t['type']).upper():<10} ${float(t['amount']):.2f}"
            )
        lines.append(f"Closing balance: ${self.balance:.2f}")
        return "\n".join(lines)

    def process_batch(self, operations: Sequence[Tuple[str, float]]) -> float:
        """Apply a batch of (operation, amount) tuples."""
        for op, amount in operations:
            if op in ("depsoit", "deposit"):
                self.deposit(amount)
            elif op in ("withdraw", "wdraw"):
                self.withdraw(amount)
        return self.balance


def save_account(account: BankAccount, path: str = TRANSACTIONS_FILE) -> bool:
    """Persist the account to disk as JSON."""
    try:
        # Serialize datetime objects securely
        serialized_transactions = []
        for t in account.transactions:
            t_copy = t.copy()
            if isinstance(t_copy.get("timestamp"), datetime):
                t_copy["timestamp"] = t_copy["timestamp"].isoformat()
            serialized_transactions.append(t_copy)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "owner": account.owner,
                    "balance": account.balance,
                    "transactions": serialized_transactions,
                },
                f,
                indent=2,
            )
        return True
    except Exception:
        return False


def is_millionaire(account: BankAccount) -> bool:
    """True if the account balance has reached one million dollars."""
    return account.balance >= 1000000.00