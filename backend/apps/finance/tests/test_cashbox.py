from datetime import date
from decimal import Decimal

from django.test import TestCase

from apps.finance.models import CashTransaction, Cashbox
from apps.finance.services import cashbox_balance


class CashboxTests(TestCase):
    def test_cashbox_balance_is_cash_in_minus_cash_out_plus_opening(self):
        cashbox = Cashbox.objects.create(name="Main", opening_balance=Decimal("100"))
        CashTransaction.objects.create(
            cashbox=cashbox,
            transaction_type="in",
            amount=Decimal("250"),
            transaction_date=date.today(),
            description="Collection",
        )
        CashTransaction.objects.create(
            cashbox=cashbox,
            transaction_type="out",
            amount=Decimal("75"),
            transaction_date=date.today(),
            description="Expense",
        )
        self.assertEqual(cashbox_balance(cashbox), Decimal("275"))
