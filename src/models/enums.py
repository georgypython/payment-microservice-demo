from enum import StrEnum


class CurrencyType(StrEnum):
    USD = "usd"
    RUB = "rub"
    EUR = "eur"


class PaymentStatus(StrEnum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
