"""Bank account management with statements and persistence."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Final, Literal, TypedDict, cast

TRANSACTIONS_FILE: Final[Path] = Path("transactions.json")
TWO_PLACES: Final[Decimal] = Decimal("0.01")


class TransactionDict(TypedDict):
    """Type definition for transaction records."""

    type: Literal["deposit", "withdrawal"]
    amount: str  # Serialized or precision string representation
    timestamp: str  # ISO 8601 string representation for persistent safety


class BankAccount:
    """A sovereign, high-performance bank account supporting deposits, withdrawals, and statements."""

    __slots__ = ("_owner", "_balance", "_transactions")

    def __init__(
        self,
        owner: str,
        balance: float | Decimal = Decimal("0.00"),
        transactions: list[TransactionDict] | None = None,
    ) -> None:
        self._owner: str = owner
        self._balance: Decimal = (
            balance
            if isinstance(balance, Decimal)
            else Decimal(str(balance))
        ).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
        
        parsed_transactions: list[TransactionDict] = []
        if transactions is not None:
            for t in transactions:
                # Ensure runtime shape and type safety
                parsed_transactions.append({
                    "type": t["type"],
                    "amount": str(Decimal(str(t["amount"])).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)),
                    "timestamp": str(t["timestamp"])
                })
        self._transactions: list[TransactionDict] = parsed_transactions

    @property
    def owner(self) -> str:
        """Get account owner."""
        return self._owner

    @property
    def balance(self) -> float:
        """Get current balance as float for legacy contract compatibility."""
        return float(self._balance)

    @property
    def balance_decimal(self) -> Decimal:
        """Get current balance with absolute precision as a Decimal."""
        return self._balance

    @property
    def transactions(self) -> list[TransactionDict]:
        """Get transaction history list."""
        return self._transactions

    def deposit(self, amount: float | Decimal) -> float:
        """Deposit funds into the account safely with absolute financial precision."""
        dec_amount = (
            amount
            if isinstance(amount, Decimal)
            else Decimal(str(amount))
        ).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)

        if dec_amount <= Decimal("0.00"):
            raise ValueError("Deposit amount must be positive")
        
        self._balance = (self._balance + dec_amount).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
        self._transactions.append(
            {
                "type": "deposit",
                "amount": str(dec_amount),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
        return float(self._balance)

    # Alias preserved for backwards compatibility with typos in older calls
    def depsoit(self, amount: float | Decimal) -> float:
        """Alias for deposit."""
        return self.deposit(amount)

    def withdraw(self, amount: float | Decimal) -> float:
        """Withdraw funds from the account securely with absolute financial precision."""
        dec_amount = (
            amount
            if isinstance(amount, Decimal)
            else Decimal(str(amount))
        ).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)

        if dec_amount <= Decimal("0.00"):
            raise ValueError("Withdrawal amount must be positive")
        if dec_amount > self._balance:
            raise ValueError("Insufficient funds")
            
        self._balance = (self._balance - dec_amount).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
        self._transactions.append(
            {
                "type": "withdrawal",
                "amount": str(dec_amount),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
        return float(self._balance)

    def wihdraw(self, amount: float | Decimal) -> float:
        """Alias for withdraw."""
        return self.withdraw(amount)

    def apply_interest(self, rate_percent: float | Decimal) -> float:
        """Apply monthly interest to the balance with exact financial precision."""
        dec_rate = (
            rate_percent
            if isinstance(rate_percent, Decimal)
            else Decimal(str(rate_percent))
        )
        interest = (self._balance * (dec_rate / Decimal("100.0"))).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
        self._balance = (self._balance + interest).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
        return float(self._balance)

    def get_statement(self) -> str:
        """Return a formatted statement of every transaction efficiently."""
        lines = [f"Statement for {self._owner}"]
        for t in self._transactions:
            ts_val = t["timestamp"]
            try:
                dt_obj = datetime.fromisoformat(ts_val)
                ts_str = dt_obj.strftime("%Y-%m-%d %H:%M")
            except (ValueError, TypeError):
                ts_str = str(ts_val)
                
            lines.append(
                f"{ts_str}  {t['type'].upper():<10} ${float(t['amount']):.2f}"
            )
        lines.append(f"Closing balance: ${float(self._balance):.2f}")
        return "\n".join(lines)

    def process_batch(self, operations: list[tuple[str, float | Decimal]]) -> float:
        """Apply a batch of (operation, amount) tuples safely."""
        for op, amount in operations:
            if op in ("depsoit", "deposit"):
                self.deposit(amount)
            elif op in ("withdraw", "wdraw", "wihdraw"):
                self.withdraw(amount)
        return float(self._balance)


def save_account(
    account: BankAccount, path: Path | str = TRANSACTIONS_FILE
) -> bool:
    """Persist the account to disk as JSON safely using modern path handling."""
    try:
        file_path = Path(path)
        with file_path.open("w", encoding="utf-8") as f:
            json.dump(
                {
                    "owner": account.owner,
                    "balance": str(account.balance_decimal),
                    "transactions": account.transactions,
                },
                f,
                indent=2,
            )
        return True
    except (OSError, TypeError, ValueError):
        return False


def is_millionaire(account: BankAccount) -> bool:
    """True if the account balance has reached one million dollars (using exact Decimal comparison)."""
    return account.balance_decimal >= Decimal("1000000.00")