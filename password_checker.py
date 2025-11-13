import re

def is_strong_password(password):
    pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()]).{8,}$'
    return re.match(pattern, password) is not None

def check_user_password():
    password = input("Введите пароль для проверки: ")
    if is_strong_password(password):
        print("Пароль надежный.")

    else:
        print("Пароль ненадежный!")

def find_strong_passwords_in_file(filename):
    try:
        with open(filename, 'r') as file:
            passwords = file.readlines()
        
        strong_passwords = []
        for password in passwords:
            password = password.strip()
            if is_strong_password(password):
                strong_passwords.append(password)
        
        if strong_passwords:
            print("Надежные пароли в файле:")
            for pwd in strong_passwords:
                print(pwd)
        else:
            print("В файле нет надежных паролей.")
    except FileNotFoundError:
        print("Файл не найден.")

if __name__ == "__main__":
    while True:
        print("1. Проверить пароль")
        print("2. Найти надежные пароли в файле")
        print("3. Выйти")
        choice = input("Выберите действие : ")
        if choice == '1':
            check_user_password()
        elif choice == '2':
            filename = input("Введите путь к файлу: ")
            find_strong_passwords_in_file(filename)
        elif choice == '3':
            break
        else:
            print("Неверный выбор.")