import telebot
from telebot import types
from config import TOKEN, MAX_COUNT_QUESTIONS, STAFF_CHAT_ID
import json
from obespechenie import WorkJSON, Quiz

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start(message):

    """
    Функция start обрабатывает команду /start, 
    которая обычно отправляется пользователем при первом 
    взаимодействии с ботом. В этой функции выполняются 
    несколько важных шагов: приветствие пользователя, отправка изображения и вызов меню.
    """

    id = message.from_user.id
    firstname = message.from_user.first_name
    with open('photo/logo.jpg', 'rb') as photo:
        bot.send_photo(id, photo, caption=f'Привет, {firstname}. Я бот Московского зоопарка')
    menu(id)



def menu(user_id):

    """
    Функция menu отвечает за отправку пользователю меню с различными кнопками, 
    которые позволяют выбрать одну из доступных опций. Каждая кнопка вызывает 
    определенную команду или действие через callback_data.
    """

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    button1 = types.InlineKeyboardButton(text='Викторина', callback_data='quiz')
    button2 = types.InlineKeyboardButton(text='Обратная связь', callback_data='feedback')
    button3 = types.InlineKeyboardButton(text='О нас', callback_data='about')
    button4 = types.InlineKeyboardButton(text='Отзывы', callback_data='ask_otzuv')
    keyboard.add(button1, button3, button2, button4)
    bot.send_message(user_id, 'Выберите нужное действие:', reply_markup=keyboard)



@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):

    """
    функция callback_query отвечает за обработку callback запросов, 
    отправляемых ботом при нажатии на кнопки в интерфейсе. 
    Когда пользователь нажимает на одну из кнопок, бот получает 
    данные callback и вызывает соответствующую функцию. 
    """

    # try:
    user_id = call.from_user.id
    if user_id != bot.get_me().id:
        if call.data == 'quiz':
            ask_start_quiz(user_id)
        if call.data == 'about':
            show_about(user_id)
        if call.data == 'feedback':
            feedback(user_id)  
        if call.data == 'menu':
            menu(user_id)
        if call.data == 'start_quiz':
            WorkJSON.add_to_bd(user_id)
            proverka_po_bd(user_id)
            send_question(user_id)
        if call.data == 'send_feedback':
            svyaz_s_sotrudnikom(user_id)
        if call.data == 'ask_otzuv':
            ask_otzuv(user_id)
        if call.data == 'write_otzuv':
            write_otzuv_sms(user_id)
    # except Exception as e:
    #     print(e)



def write_otzuv_sms(id):

    """
    Функция write_otzuv_sms отправляет пользователю 
    запрос на написание отзыва и после этого регистрирует 
    обработчик для получения следующего сообщения от пользователя, 
    которое будет обработано функцией write_otzuv.
    """

    bot.send_message(id, 'Напишите пожалуйста отзыв')
    bot.register_next_step_handler_by_chat_id(id, write_otzuv)



def write_otzuv(message):

    """
    Функция write_otzuv записывает отзыв пользователя в базу данных 
    (в данном случае в файл klients.json) и отправляет благодарственное 
    сообщение пользователю, а затем возвращает его в главное меню.
    """
    user_id = str(message.from_user.id)
    klients = WorkJSON.load_json('klients.json')
    klients[user_id]["otzuv"] = message.text
    WorkJSON.save_json('klients.json', klients)
    bot.send_message(message.from_user.id, 'Спасибо за Ваш отзыв!')
    menu(message.from_user.id)


def ask_otzuv(id):
    
    """
    Эта функция используется для отправки пользователю сообщения с вопросом, 
    хочет ли он оставить отзыв, и предоставляет две интерактивные кнопки 
    для ответа: "Да" и "Вернуться в меню".
    """
    if WorkJSON.proverka(id):
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        button1 = types.InlineKeyboardButton(text='Да', callback_data='write_otzuv')
        button2 = types.InlineKeyboardButton(text='Вернуться в меню', callback_data='menu')
        keyboard.add(button1, button2)
        bot.send_message(id, 'Хотите написать отзыв?', reply_markup=keyboard)
    else:
        bot.send_message(id, 'Вы сможете написать отзыв только после прохождения викторины')
        menu(id)

def ask_start_quiz(id):
    
    """
    Эта функция отображает сообщение с двумя кнопками пользователю, 
    чтобы предложить ему начать викторину или вернуться в главное меню.
    """

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button1 = types.InlineKeyboardButton('Да', callback_data='start_quiz')
    button2 = types.InlineKeyboardButton('Вернуться в меню', callback_data='menu')
    keyboard.add(button1, button2)
    bot.send_message(id, f'Желаете начать викторину?', reply_markup=keyboard)



def show_about(id):

    """
    Эта функция отправляет пользователю информацию о зоопарке, 
    включая фотографию, текстовое описание и кнопки для перехода 
    на сайт или возврата в главное меню.
    """

    data = WorkJSON.load_json('about_zoo.json')
    photo = open(data['zoo']['photo'], 'rb')
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    button1 = types.InlineKeyboardButton(text='Перейти на сайт', url = data['zoo']['link'])
    button2 = types.InlineKeyboardButton(text='Вернуться в меню', callback_data='menu')
    keyboard.add(button1, button2)
    bot.send_photo(id, photo, caption=data['zoo']['text'], reply_markup=keyboard)



def feedback(id):

    """
    Эта функция позволяет пользователю запросить обратную связь с сотрудником. 
    Пользователь получает вопрос, а также кнопки для ответа — связаться с сотрудником 
    или вернуться в главное меню.
    """
    user_id = str(id)
    if WorkJSON.proverka(user_id):
        keyboard = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton(text='Да', callback_data='send_feedback')
        button2 = types.InlineKeyboardButton(text='Вернуться в меню', callback_data='menu')
        keyboard.add(button1, button2)
        bot.send_message(id, text='Вы хотите связаться с сотрудником?', reply_markup=keyboard) 
    else:
        bot.send_message(id, 'Вы сможете написать связаться с сотрудником после прохождения викторины')
        menu(id)


def proverka_po_bd(id):

    """
    Функция proverka_po_bd проверяет наличие пользователя
    в базе данных и, если пользователь не найден, добавляет
    его в базу данных с помощью метода add_to_bd из класса WorkJSON.
    """

    id = str(id)
    klients = WorkJSON.load_json('klients.json')
    if id not in klients:
        WorkJSON.add_to_bd(id)



def send_question(id):

    """
    Функция send_question отвечает за отправку вопроса пользователю 
    и отображение вариантов ответов на клавиатуре, а также подготовку 
    к обработке следующего шага (ответа пользователя) с помощью handle_answer.
    """

    user_id = str(id)
    otvetu = Quiz.vuvod_otvetov(user_id)
    markup = types.ReplyKeyboardMarkup(row_width=len(otvetu), resize_keyboard=True)
    for otvet in otvetu:
        markup.add(types.KeyboardButton(f"{otvet}"))
    bot.send_message(id, Quiz.question(id), reply_markup=markup)
    bot.register_next_step_handler_by_chat_id(id, handle_answer)



def handle_answer(message):

    """
    Функция handle_answer отвечает за обработку ответа пользователя
    в процессе викторины. После того как пользователь выбирает вариант ответа,
    эта функция выполняет проверку правильности ответа, сохраняет его в базу данных
    и продолжает викторину или завершает её, если это последний вопрос.
    """

    user_id = message.from_user.id
    user_answer = message.text
    questions = WorkJSON.load_json('que.json')
    current_question_number = Quiz.get_nomer_voprosa(user_id)
    valid_answers = questions["answers"][current_question_number]
    if user_answer not in valid_answers:
        bot.send_message(user_id , 'Пожалуйста, выберите один из предложенных вариантов.')
        send_question(user_id)
        return
    klients = WorkJSON.load_json('klients.json')
    klients[str(user_id)]["answers"].append(questions["answers"][current_question_number][user_answer])
    WorkJSON.save_json('klients.json', klients)
    if int(current_question_number) < MAX_COUNT_QUESTIONS:
        Quiz.uvel_vopr(user_id)
        send_question(user_id)  # Отправляем следующий вопрос
    else:
        finish_quiz(user_id)



def finish_quiz(id):

    """
    Функция finish_quiz завершает викторину, подводит итоги 
    и отправляет пользователю результат. Также она генерирует 
    кнопки для взаимодействия с пользователем, включая возможность 
    повторно пройти викторину или поделиться результатом.
    """

    bot.send_message(id, 'Квиз завершён! Спасибо за участие!\nПодсчитываю результаты...', reply_markup=types.ReplyKeyboardRemove(), parse_mode='Markdown')
    animal_name = Quiz.podschet_rezultatov(id)
    bot.send_message(id, f'Поздравляю! Вы - {animal_name}')
        # Открываем файл animals.json для чтения
    animals = WorkJSON.load_json('animals.json')
    # Получаем название животного, подходящего для пользователя
    # Извлекаем данные для этого животного
    animal_data = animals.get(animal_name)
    Quiz.zapis_rezultata(id)
    # Получаем ссылку на фото и текст
    if animal_data:
        photo_path = animal_data["photo"]  # Путь к изображению
        text = animal_data["text"]

        keyboard = types.InlineKeyboardMarkup(row_width=1)
        button1 = types.InlineKeyboardButton(text='Вернуться в меню', callback_data='menu')
        button2 = types.InlineKeyboardButton(text='Перепройти викторину', callback_data='start_quiz')
        button3 = types.InlineKeyboardButton(text='Поделиться результатом в ВК', url=Quiz.generate_share_links(id))
        keyboard.add(button1, button2, button3)
        
        # Отправка локального изображения
        with open(photo_path, 'rb') as photo_file:
            bot.send_photo(id, photo_file, caption=text, reply_markup=keyboard)
        Quiz.oblulenie_voprosov(id)
    else:
        bot.send_message(id, "Не удалось найти информацию о животном.")



def svyaz_s_sotrudnikom(id):

    """
    Функция svyaz_s_sotrudnikom обрабатывает запрос пользователя 
    на связь с сотрудником, собирая информацию о пользователе, 
    включая его результат викторины и отзыв, а затем отправляет 
    эту информацию сотруднику для дальнейшей обработки. После этого 
    она уведомляет пользователя о том, что запрос был отправлен.
    """

    try:
        # Загружаем данные пользователей
        klients = WorkJSON.load_json('klients.json')
    except (FileNotFoundError, json.JSONDecodeError):
        bot.send_message(id, 'Ошибка: данные пользователей недоступны.')
        return
    user_id = str(id)

    # Получаем результат викторины
    rezult = klients[user_id].get('rezultat', 'Отсутствует')
    otzuv = klients[user_id].get('otzuv', 'Отсутствует')
    # Получаем информацию о пользователе
    try:
        chat = bot.get_chat(id)
        username = chat.username if chat.username else chat.first_name
    except Exception as e:
        bot.send_message(id, 'Ошибка: не удалось получить информацию о пользователе.')
        print(f"Ошибка получения имени пользователя: {e}")
        return
    # Отправляем сообщение сотруднику
    bot.send_message(STAFF_CHAT_ID, f'Пользователь @{username}\nРезультат викторины: {rezult}\nОтзыв: {otzuv}\nЗапрос на обратную связь')
    bot.send_message(id, 'Запрос сотруднику отправлен')
    menu(id)

@bot.message_handler(func=lambda message: True)
def false(message):
    """
    Функция false является обработчиком сообщений в боте, 
    который реагирует на любые сообщения, отправленные пользователями. 
    Она выполняет определённое действие, если не были удовлетворены другие условия обработки 
    (например, если не была найдена подходящая команда или сообщение).
    """
    bot.send_message(message.chat.id, 'Нет доступных команд.')


bot.polling()
