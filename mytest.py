from account import Account

my_acc = Account("Тестовый Пользователь", 500)
my_acc.deposit(250)
print(my_acc.get_history(as_text=True))