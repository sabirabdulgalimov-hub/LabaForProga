import unittest
from password_checker import is_strong_password

class TestPasswordChecker(unittest.TestCase):
    def test_strong_password(self):
        self.assertTrue(is_strong_password("Secure123!"))
        self.assertTrue(is_strong_password("Secure123434!"))
    
    def test_missing_lowercase(self):
        self.assertFalse(is_strong_password("SECURE123!"))
    
    def test_missing_uppercase(self):
        self.assertFalse(is_strong_password("secure123!"))
    
    def test_missing_digit(self):
        self.assertFalse(is_strong_password("Secure!!!"))
    
    def test_missing_special_char(self):
        self.assertFalse(is_strong_password("Secure123"))
    
    def test_too_short(self):
        self.assertFalse(is_strong_password("Sec1!"))

if __name__ == '__main__':
    # Запускаем тесты
    unittest.main(exit=False)
    
    # Ждем подтверждения выхода
    while True:
        response = input("\nХотите выйти? (y/n): ").strip().lower()
        if response in ['y', 'yes', 'д', 'да']:
            print("Выход из программы...")
            break
        elif response in ['n', 'no', 'н', 'нет']:
            print("Продолжаем работу...")
            # Можно добавить повторный запуск тестов или другие действия
            break
        else:
            print("Пожалуйста, введите 'y' для выхода или 'n' для продолжения.")