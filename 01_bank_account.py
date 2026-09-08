"""Bank account management with statements and persistence."""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple, Union

TRANSACTIONS_FILE: str = "transactions.json"


class BankAccount:
    """A bank account supporting deposits, withdrawals, statements, and batch processing."""

    __slots__ = ("owner", "balance", "transactions")

    def __init__(
        self,
        owner: str,
        balance: float = 0.0,
        transactions: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """Initialize a BankAccount with an owner, initial balance, and optional transaction history."""
        if balance < 0:
            raise ValueError("Initial balance cannot be negative")
        self.owner: str = str(owner)
        self.balance: float = float(balance)
        self.transactions: List[Dict[str, Any]] = list(transactions) if transactions is not None else []

    def deposit(self, amount: float) -> float:
        """Deposit funds into the account."""
        if not isinstance(amount, (int, float)) or amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self.balance += float(amount)
        self.transactions.append(
            {"type": "deposit", "amount": float(amount), "timestamp": datetime.now()}
        )
        return self.balance

    # Alias for legacy compatibility
    depsoit = deposit

    def withdraw(self, amount: float) -> float:
        """Withdraw funds from the account."""
        if not isinstance(amount, (int, float)) or amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        self.balance -= float(amount)
        self.transactions.append(
            {"type": "withdrawal", "amount": float(amount), "timestamp": datetime.now()}
        )
        return self.balance

    # Alias for legacy typo compatibility
    wihdraw = withdraw

    def apply_interest(self, rate_percent: float) -> float:
        """Apply monthly interest to the balance."""
        if not isinstance(rate_percent, (int, float)):
            raise TypeError("Interest rate must be numeric")
        self.balance += self.balance * (float(rate_percent) / 100.0)
        return self.balance

    def get_statement(self) -> str:
        """Return a formatted statement of every transaction."""
        lines: List[str] = [f"Statement for {self.owner}"]
        for t in self.transactions:
            ts = t.get("timestamp")
            if isinstance(ts, datetime):
                ts_str = f"{ts:%Y-%m-%d %H:%M}"
            elif isinstance(ts, str):
                try:
                    parsed_dt = datetime.fromisoformat(ts)
                    ts_str = f"{parsed_dt:%Y-%m-%d %H:%M}"
                except ValueError:
                    ts_str = ts[:16]
            else:
                ts_str = "N/A             "
            
            tx_type = str(t.get("type", "UNKNOWN")).upper()
            amount = float(t.get("amount", 0.0))
            lines.append(f"{ts_str}  {tx_type:<10} ${amount:.2f}")
        lines.append(f"Closing balance: ${self.balance:.2f}")
        return "\n".join(lines)

    def process_batch(self, operations: Iterable[Union[Tuple[str, float], Sequence[Any]]]) -> float:
        """Apply a batch of (operation, amount) tuples."""
        dispatch = {
            "deposit": self.deposit,
            "depsoit": self.deposit,
            "withdraw": self.withdraw,
            "wdraw": self.withdraw,
            "wihdraw": self.withdraw,
        }
        for op, amount in operations:
            handler = dispatch.get(str(op).lower())
            if handler is None:
                raise ValueError(f"Unknown operation: {op}")
            handler(amount)
        return self.balance


def _json_serial(obj: Any) -> Any:
    """JSON serializer for objects not serializable by default."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


def save_account(account: BankAccount, path: Union[str, Path] = TRANSACTIONS_FILE) -> bool:
    """Persist the account to disk as JSON atomically and safely."""
    target_path = Path(path)
    try:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "owner": account.owner,
            "balance": account.balance,
            "transactions": account.transactions,
        }
        json_data = json.dumps(payload, default=_json_serial, indent=2)
        
        # Atomic file write to avoid file corruption on interruption
        with tempfile.NamedTemporaryFile(
            "w", dir=target_path.parent, delete=False, encoding="utf-8"
        ) as tf:
            tf.write(json_data)
            temp_name = tf.name
        os.replace(temp_name, target_path)
        return True
    except Exception:
        return False


def is_millionaire(account: BankAccount) -> bool:
    """Return True if the account balance has reached or exceeded one million dollars."""
    return account.balance >= 1_000_000.00