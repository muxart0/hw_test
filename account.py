from datetime import datetime
from typing import List, Dict, Any, Optional


class Account:
    """
    Базовый класс, моделирующий поведение банковского счёта.
    Обеспечивает хранение баланса, выполнение базовых операций и ведение истории.
    """

    def __init__(self, account_holder: str, balance: float = 0.0) -> None:
        """
        Инициализирует новый банковский счёт.

        :param account_holder: Имя владельца счёта.
        :param balance: Начальный баланс (по умолчанию 0.0, не может быть отрицательным).
        """
        if not account_holder or not isinstance(account_holder, str):
            raise ValueError("Имя владельца счёта должно быть непустой строкой.")
        if balance < 0:
            raise ValueError("Начальный баланс обычного счёта не может быть отрицательным.")

        self.holder: str = account_holder
        self._balance: float = float(balance)
        self.operations_history: List[Dict[str, Any]] = []

    def _record_operation(
        self,
        op_type: str,
        amount: float,
        status: str,
        extra_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Вспомогательный защищённый метод для фиксации операции в истории.
        """
        record: Dict[str, Any] = {
            'type': op_type,
            'amount': float(amount),
            'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'balance_after': self._balance,
            'status': status
        }
        if extra_info:
            record.update(extra_info)

        self.operations_history.append(record)
        return record

    def deposit(self, amount: float) -> bool:
        """
        Пополняет счёт на указанную сумму.

        :param amount: Сумма пополнения (должна быть строго больше 0).
        :return: True при успешной операции, False при ошибке.
        """
        if amount <= 0:
            self._record_operation('deposit', amount, 'fail')
            return False

        self._balance += amount
        self._record_operation('deposit', amount, 'success')
        return True

    def withdraw(self, amount: float) -> bool:
        """
        Снимает средства со счёта.

        :param amount: Сумма снятия (должна быть строго больше 0).
        :return: True при успешной операции, False при нехватке средств или неверной сумме.
        """
        if amount <= 0 or amount > self._balance:
            self._record_operation('withdraw', amount, 'fail')
            return False

        self._balance -= amount
        self._record_operation('withdraw', amount, 'success')
        return True

    def get_balance(self) -> float:
        """
        Возвращает текущий баланс счёта.
        """
        return self._balance

    def get_history(self, as_text: bool = False) -> Any:
        """
        Возвращает историю операций.

        :param as_text: Если True, возвращает красиво отформатированную строку,
                        иначе — копию списка словарей.
        """
        if not as_text:
            return self.operations_history.copy()

        if not self.operations_history:
            return f"История операций по счёту {self.holder} пуста."

        lines = [f"=== История операций: {self.holder} ==="]
        for idx, op in enumerate(self.operations_history, 1):
            credit_note = ""
            if 'credit_used' in op:
                credit_note = f" | Кредитные средства: {'Да' if op['credit_used'] else 'Нет'}"

            line = (
                f"{idx}. [{op['datetime']}] {op['type'].upper()} | "
                f"Сумма: {op['amount']:.2f} | Статус: {op['status'].upper()} | "
                f"Баланс: {op['balance_after']:.2f}{credit_note}"
            )
            lines.append(line)
        return "\n".join(lines)

    def get_analytics(self) -> Dict[str, Any]:
        """
        Предоставляет базовую аналитику по истории операций.
        """
        total_deposited = sum(
            op['amount'] for op in self.operations_history
            if op['type'] == 'deposit' and op['status'] == 'success'
        )
        total_withdrawn = sum(
            op['amount'] for op in self.operations_history
            if op['type'] == 'withdraw' and op['status'] == 'success'
        )
        failed_ops = sum(
            1 for op in self.operations_history if op['status'] == 'fail'
        )

        return {
            'total_operations': len(self.operations_history),
            'total_deposited': total_deposited,
            'total_withdrawn': total_withdrawn,
            'failed_operations': failed_ops,
            'current_balance': self._balance
        }


class CreditAccount(Account):
    """
    Класс кредитного счёта, наследующий функциональность базового класса Account.
    Позволяет уходить в минус в пределах заданного кредитного лимита.
    """

    def __init__(
        self,
        account_holder: str,
        balance: float = 0.0,
        credit_limit: float = 0.0
    ) -> None:
        """
        Инициализирует кредитный счёт.

        :param account_holder: Имя владельца счёта.
        :param balance: Начальный баланс (не может быть ниже -credit_limit).
        :param credit_limit: Кредитный лимит (не может быть отрицательным).
        """
        if credit_limit < 0:
            raise ValueError("Кредитный лимит не может быть отрицательным.")
        if balance < -credit_limit:
            raise ValueError("Начальный баланс не может быть ниже кредитного лимита.")

        # Инициализируем родительский класс с 0.0, чтобы обойти запрет
        # на отрицательный стартовый баланс для базового счёта
        super().__init__(account_holder, 0.0)
        self._balance = float(balance)
        self._credit_limit: float = float(credit_limit)

    def get_available_credit(self) -> float:
        """
        Показывает, сколько всего средств (собственных + кредитных) доступно для снятия.
        Вычисляется по формуле: текущий баланс + кредитный лимит.
        """
        return self._balance + self._credit_limit

    def deposit(self, amount: float) -> bool:
        """
        Пополняет кредитный счёт и фиксирует, использовались ли кредитные средства
        (погашался ли кредитный долг в процессе операции).
        """
        if amount <= 0:
            self._record_operation(
                'deposit', amount, 'fail', {'credit_used': False}
            )
            return False

        # Если до пополнения баланс был отрицательным, операция затрагивает кредитный лимит
        used_credit = self._balance < 0
        self._balance += amount
        self._record_operation(
            'deposit', amount, 'success', {'credit_used': used_credit}
        )
        return True

    def withdraw(self, amount: float) -> bool:
        """
        Снимает средства с учётом кредитного лимита и фиксирует в истории,
        были ли задействованы кредитные средства.
        """
        if amount <= 0:
            self._record_operation(
                'withdraw', amount, 'fail', {'credit_used': False}
            )
            return False

        # Проверяем, не превышает ли сумма доступный остаток (баланс + лимит)
        if self._balance - amount < -self._credit_limit:
            self._record_operation(
                'withdraw', amount, 'fail', {'credit_used': False}
            )
            return False

        # Кредитные средства задействуются, если после снятия баланс становится меньше 0
        used_credit = (self._balance - amount) < 0
        self._balance -= amount
        self._record_operation(
            'withdraw', amount, 'success', {'credit_used': used_credit}
        )
        return True
      

if __name__ == "__main__":
    # 1. Тестирование базового счёта Account
    print("--- Тест базового счёта ---")
    acc = Account("Иван Иванов", 1000)
    acc.deposit(500)        # Успешно: баланс 1500
    acc.withdraw(300)       # Успешно: баланс 1200
    acc.withdraw(2000)      # Ошибка (недостаточно средств): баланс 1200, статус 'fail'
    acc.deposit(-100)       # Ошибка (отрицательная сумма): статус 'fail'

    print(f"Текущий баланс Ивана: {acc.get_balance()}")
    print(acc.get_history(as_text=True))
    print("Аналитика:", acc.get_analytics())
    print("\n" + "=" * 50 + "\n")

    # 2. Тестирование кредитного счёта CreditAccount
    print("--- Тест кредитного счёта ---")
    credit_acc = CreditAccount("Анна Смирнова", balance=500, credit_limit=1000)
    print(f"Доступно средств с учётом кредита: {credit_acc.get_available_credit()}")

    credit_acc.withdraw(300)   # Снятие своих средств (остаток 200, credit_used: False)
    credit_acc.withdraw(600)   # Уход в кредит (остаток -400, credit_used: True)
    credit_acc.withdraw(1000)  # Превышение лимита (остаток -400, статус: 'fail')
    credit_acc.deposit(500)    # Погашение кредита и выход в плюс (остаток 100, credit_used: True)

    print(f"Текущий баланс Анны: {credit_acc.get_balance()}")
    print(f"Доступно средств с учётом кредита: {credit_acc.get_available_credit()}")
    print(credit_acc.get_history(as_text=True))
