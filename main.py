import telebot
import logging
import json
import random

from config import api_token

TOKEN = api_token

bot = telebot.TeleBot(TOKEN)

try:
    with open("user_data1.json", "r", encoding="utf-8") as file:
        user_data = json.load(file)
except FileNotFoundError:
    user_data = {}

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Hi!")

@bot.message_handler(commands=['learn'])
def handle_learn(message):
    user_words = user_data.get(str(message.chat.id), {})
    if not user_words:
        bot.send_message(message.chat.id, "Файл со словами пуст! Добавьте слова на /addword (слово на русс.яз) (его перевод на англ.яз)!")
        return
    if len(message.text.split()) == 2:
        if float(message.text.split()[1]) % 1 == 0:
            if int(message.text.split()[1]) <= 20 and int(message.text.split()[1]) > 0:
                words_number = int(message.text.split()[1])
                correct_words = 0
                ask_translation(message.chat.id, user_words, words_number, correct_words, words_number)
            else:
                bot.send_message(message.chat.id, "Ошибка! Введите число от 1 до 20!")
        else:
                bot.send_message(message.chat.id, "Ошибка! Введите целое число!")
    else:
        bot.send_message(message.chat.id, "Неправильный ввод! Попробуйте вписать так: /learn 5 <-- или любое другое число не превышающее 20.")

def ask_translation(chat_id, user_words, words_left, correct_words, words_number):
    if words_left > 0:
        word = random.choice(list(user_words.keys()))
        translation = user_words[word]
        bot.send_message(chat_id, f"Напиши перевод слова {word}.")
        bot.register_next_step_handler_by_chat_id(chat_id, check_translation, translation, words_left, correct_words, words_number)
    else:
        bot.send_message(chat_id, f"Урок закончен! Правильных ответов: {correct_words} из {words_number} возможных.")

def check_translation(message, expected_translation, words_left, correct_words, words_number):
    user_translation = message.text.strip().lower()
    if user_translation == expected_translation.lower():
        bot.send_message(message.chat.id, "Правильно!")
        correct_words += 1
    else:
        bot.send_message(message.chat.id, f"Неправильно :( Вот перевод: {expected_translation}.")
    
    words_left -= 1
    ask_translation(message.chat.id, user_data[str(message.chat.id)], words_left, correct_words, words_number)


@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(message.chat.id, "-- Бот для изучения англ.яз --\nЗапросы: как тебя зовут?; \nрасскажи о себе; \nкак дела?")

@bot.message_handler(commands=['addword'])
def handle_addword(message):
    global user_data 
    chat_id = message.chat.id
    user_dict = user_data.get(chat_id, {})

    words = message.text.split()[1:] 
    print(words)
    if len(words) == 2:
        word, translation = words[0].lower(), words[1].lower()
        user_dict[word] = translation

        user_data[chat_id] = user_dict

        with open("user_data.json", "w", encoding="utf-8") as file:
            json.dump(user_data, file, ensure_ascii=False, indent=4)
        bot.send_message(message.chat.id, "Добавлено в словарь")
    else:
        bot.send_message(message.chat.id, "Ошибка")
        

@bot.message_handler(func=lambda message: True)
def handle_all(message):
    if message.text.lower() == "как тебя зовут?":
        bot.send_message(message.chat.id, "E-1321")
    elif message.text.lower() == "расскажи о себе":
        bot.send_message(message.chat.id, "Я бот для изучение чего-то")
    elif message.text.lower() == "как дела?":
        bot.send_message(message.chat.id, "Хорошо, а у тебя как?")
    else:
        bot.send_message(message.chat.id, "Я занят!!!")
        
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("Бот запущен!")
    bot.polling(non_stop=True)