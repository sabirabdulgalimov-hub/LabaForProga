import telebot
from telebot import types
import requests
import xml.etree.ElementTree as ET

bot = telebot.TeleBot('ТОКЕН')

# Словарь для хранения состояния пользователя
user_states = {}

def get_valyt(currency_name: str, date: str = None):
    """Получает курс валюты по названию с сайта ЦБ"""
    url = "https://www.cbr.ru/scripts/XML_daily.asp"

    if date and date != 'Сегодня':
        url += f"?date_req={date}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        
        # Получаем дату курсов
        date_from_xml = root.attrib.get('Date', 'Неизвестно')
        
        # Ищем валюту по названию (точное совпадение)
        for valute in root.findall('Valute'):
            name_in_xml = valute.find('Name').text
            if currency_name == name_in_xml:  # Точное совпадение
                value_text = valute.find('Value').text  # "98,5678"
                nominal = valute.find('Nominal').text
                vunit_rate_element = valute.find('VunitRate')
                
                # Преобразуем значение в число для расчетов
                value_num = float(value_text.replace(',', '.'))
                
                # Рассчитываем курс за 1 единицу
                rate = float(nominal) / value_num
                
                # Обрабатываем VunitRate если он есть
                vunit_rate = None
                if vunit_rate_element is not None and vunit_rate_element.text:
                    vunit_rate = float(vunit_rate_element.text.replace(',', '.'))

                nominal_text = valute.find('Nominal').text
                nominal_num = float (nominal_text.replace(',', '.'))

                if nominal_num > 1:
                    nominal_num = nominal_num
                else:
                    nominal_num = None

                # Форматируем значение для отображения (округляем и заменяем точку на запятую)
                value_display = f"{value_num:.2f}".replace('.', ',')
                
                return {
                    'rate': round(rate, 2),
                    'nominal': nominal_num,
                    'date': date_from_xml,
                    'value': value_display,  
                    'VunitRate': vunit_rate
                }
        return None
    except Exception as e:
        print(f"Ошибка при получении курса: {e}")
        return None

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Выбрать валюту')
    btn2 = types.KeyboardButton('Информация о боте')
    markup.add(btn1, btn2)
    
    # Очищаем состояние пользователя
    if message.chat.id in user_states:
        del user_states[message.chat.id]
    
    bot.send_message(message.chat.id, 'Выберите действие:', reply_markup=markup)

def show_currencies(message):
    """Показывает клавиатуру для выбора валюты"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Белорусский рубль')
    btn2 = types.KeyboardButton('Тенге')
    btn3 = types.KeyboardButton('Доллар США')
    btn4 = types.KeyboardButton('Евро')
    btn5 = types.KeyboardButton('Юань')
    btn6 = types.KeyboardButton('Индийских рупий')

    btn_back = types.KeyboardButton('Назад')
    
    markup.row(btn1, btn2, btn3)
    markup.row(btn4, btn5, btn6)
    markup.add(btn_back)
    
    # Сохраняем состояние - пользователь выбирает валюту
    user_states[message.chat.id] = {'step': 'choosing_currency'}
    
    bot.send_message(message.chat.id, 'Выберите валюту:', reply_markup=markup)

def ask_for_date(message, currency):
    """Запрашивает дату для выбранной валюты"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Сегодня')
    btn_back = types.KeyboardButton('Назад')
    
    markup.row(btn1)
    markup.add(btn_back)
    
    # Сохраняем выбранную валюту и переходим к выбору даты
    user_states[message.chat.id] = {
        'step': 'choosing_date',
        'currency': currency
    }
    
    bot.send_message(message.chat.id, 
                    f'Вы выбрали: {currency}\n\n'
                    'Выберите дату или напишите ее в формате ДД/ММ/ГГГГ (например, 23/01/2024):', 
                    reply_markup=markup)

@bot.message_handler(content_types=['text'])
def handle_text(message):
    chat_id = message.chat.id
    
    if message.text == 'Выбрать валюту':
        show_currencies(message)
        
    elif message.text == 'Информация о боте':
        bot.send_message(chat_id, 
                        'Бот создан Абдулгалимовым Сабиром\n'
                        'Группа ИДБ 24-11\n'
                        'Бот использует данные с ЦБР')
    
    # Обработка выбора валюты
    elif message.text in ['Белорусский рубль', 'Тенге', 'Доллар США', 'Евро', 'Юань', 'Индийских рупий']:
        ask_for_date(message, message.text)
    
    # Обработка выбора даты
    elif chat_id in user_states and user_states[chat_id].get('step') == 'choosing_date':
        date = message.text
        
        # Если выбрана кнопка "Назад" - возвращаемся к выбору валюты
        if date == 'Назад':
            show_currencies(message)
            return
            
        # Получаем сохраненную валюту
        currency = user_states[chat_id].get('currency')
        
        # Получаем курс валюты
        rate_info = get_valyt(currency, date if date != 'Сегодня' else None)
        
        if rate_info:
            # Форматируем ответ
            response = (f"📅 Дата: {rate_info['date']}\n"
                       f"💰 Валюта: {currency}\n"
                       f"📈 За 1 руб: {rate_info['rate']} {currency}.")
            if rate_info['nominal'] is not None:
                response += f"\n💵 Курс за {rate_info['nominal']} {currency}:{rate_info['value']} руб."
            # Проверяем наличие VunitRate и показываем обратное значение
            if rate_info['VunitRate'] is not None:
                response += f"\n📊 Курс за 1 {currency}: {rate_info['VunitRate']:.2f} руб."
        else:
            response = f"❌ Не удалось получить курс для {currency} на указанную дату.\nПроверьте правильность ввода даты."
        
        # Отправляем результат и возвращаем в главное меню
        bot.send_message(chat_id, response)
        start(message)
        
        # Очищаем состояние
        if chat_id in user_states:
            del user_states[chat_id]
    
    elif message.text == 'Назад':
        # Возвращаемся к главному меню
        start(message)
    
    else:
        # Если сообщение не распознано
        bot.send_message(chat_id, "Не понимаю команду. Используйте кнопки меню.")

if __name__ == "__main__":
    bot.polling(none_stop=True)