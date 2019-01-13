# coding: utf-8
# Импортирует поддержку UTF-8.
from __future__ import unicode_literals

# Импортируем модули для работы с JSON и логами.
import json
import logging
import random

# Импортируем подмодули Flask для запуска веб-сервиса.
from flask import Flask, request
app = Flask(__name__)


logging.basicConfig(level=logging.DEBUG)

# Хранилище данных о сессиях.
sessionStorage = {}

en_ru_dict = {
    'work': 'работа',
    'home': 'дом'
}

users_known_words = {}

users_current_word = {}

# Задаем параметры приложения Flask.
@app.route("/", methods=['POST'])
def main():
# Функция получает тело запроса и возвращает ответ.
    logging.info('Request: %r', request.json)

    response = {
        "version": request.json['version'],
        "session": request.json['session'],
        "response": {
            "end_session": False
        }
    }

    handle_dialog(request.json, response)

    logging.info('Response: %r', response)

    return json.dumps(
        response,
        ensure_ascii=False,
        indent=2
    )

@app.route("/ping", methods=['GET'])
def ping():
    return json.dumps(
        {'pong': 'ПОНГ'}
    )


# Функция для непосредственной обработки диалога.
def handle_dialog(req, res):
    user_id = req['session']['user_id']

    if req['session']['new']:
        # Это новый пользователь.
        # Инициализируем сессию и поприветствуем его.

        sessionStorage[user_id] = {
            'suggests': [
                "Давай.",
                "Да.",
                "Не хочу.",
                "Не буду.",
                "Отстань!",
            ]
        }

        users_known_words[user_id] = set()

        res['response']['text'] = 'Привет! Давай учить слова!'
        res['response']['buttons'] = get_suggests(user_id)
        return

    # Обрабатываем ответ пользователя.
    if req['request']['original_utterance'].lower() in [
        'ладно',
        'да',
        'давай',
    ]:
        en_word = get_new_word(user_id)
        users_current_word[user_id] = en_word
        res['response']['text'] = '{en_word} по русски {en_ru_dict[en_word]}'
        return

    response_text = ''

    user_answer = req['request']['original_utterance']
    if user_answer == en_ru_dict[users_current_word[user_id]]:
        response_text += 'Отлично.'
    else:
        response_text += 'Не верно.'

    en_word = get_new_word(user_id)
    users_current_word[user_id] = en_word
    res['response']['text'] = '{en_word} по русски {en_ru_dict[en_word]}'
    return
    # res['response']['buttons'] = get_suggests(user_id)

def get_new_word(user_id):
    for i in range(en_ru_dict.keys()):
        known_words = users_known_words[user_id]
        key = random.choice(en_ru_dict.keys())
        if key not in known_words:
            return key

    return None


# Функция возвращает две подсказки для ответа.
def get_suggests(user_id):
    session = sessionStorage[user_id]

    # Выбираем две первые подсказки из массива.
    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests']
    ]

    # Убираем первую подсказку, чтобы подсказки менялись каждый раз.
    # session['suggests'] = suggests
    # sessionStorage[user_id] = session

    # Если осталась только одна подсказка, предлагаем подсказку
    # со ссылкой на Яндекс.Маркет.
    # if len(suggests) < 2:
    #     suggests.append({
    #         "title": "Ладно",
    #         "url": "https://market.yandex.ru/search?text=слон",
    #         "hide": True
    #     })

    return suggests