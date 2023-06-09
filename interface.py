# импорты
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from config import community_token, access_token
from core import VkTools
from data_store import Database, engine


# отправка сообщений
class BotInterface:
    def __init__(self, community_token, access_token):
        self.vk = vk_api.VkApi(token=community_token)
        self.longpoll = VkLongPoll(self.vk)
        self.vk_tools = VkTools(access_token)
        self.data_base = Database()
        self.params = {}  # параметры для получения данных о пользователе
        self.worksheets = []  # список вариантов
        self.offset = 0  # смещение начала запроса

    def message_send(self, user_id, message, keyboard, attachment=None):
        self.vk.method('messages.send',
                       {'user_id': user_id,
                        'message': message,
                        'attachment': attachment,
                        'random_id': get_random_id(),
                        'keyboard': keyboard})

        # обработка событий / получение сообщений

    def event_handler(self):
        """Кнопки"""
        buttons = ['Привет', 'Поиск', 'Пока']
        button_colors = [VkKeyboardColor.SECONDARY, VkKeyboardColor.SECONDARY, VkKeyboardColor.SECONDARY]
        keyboard = self.chat_keyboard(buttons, button_colors)
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if event.text.lower() == 'привет':
                    """Логика для получения данных о пользователе"""
                    self.params = self.vk_tools.get_profile_info(event.user_id)
                    if self.params is not None:
                        if not self.params['city']:
                            self.message_send(event.user_id, f'Привет, {self.params["name"]}, введите название вашего '
                                                             'города проживания:', keyboard=keyboard.get_keyboard())
                            while True:
                                for event_ in self.longpoll.listen():
                                    if event_.type == VkEventType.MESSAGE_NEW and event_.to_me:
                                        self.params['city'] = event_.text
                                        break
                        elif not self.params['sex']:
                            self.message_send(event.user_id, 'Введите ваш пол:', keyboard=keyboard.get_keyboard())
                            self.params['sex'] = 2 if event.text == 'Мужской' else 1
                            while True:
                                for event_ in self.longpoll.listen():
                                    if event_.type == VkEventType.MESSAGE_NEW and event_.to_me:
                                        self.params['sex'] = event_.text
                                        break
                        elif not self.params['year']:
                            self.message_send(event.user_id, 'Введите ваш возраст:', keyboard=keyboard.get_keyboard())
                            self.params['year'] = event.text
                            while True:
                                for event_ in self.longpoll.listen():
                                    if event_.type == VkEventType.MESSAGE_NEW and event_.to_me:
                                        self.params['year'] = event_.text
                                        break
                        elif not self.params['relation'] or self.params['relation'] is None:
                            self.message_send(event.user_id, 'Введите ваши отношении:',
                                              keyboard=keyboard.get_keyboard())
                            self.params['relation'] = event.text
                            while True:
                                for event_ in self.longpoll.listen():
                                    if event_.type == VkEventType.MESSAGE_NEW and event_.to_me:
                                        self.params['relation'] = event_.text
                                        break
                        else:
                            self.message_send(event.user_id, f'Привет, {self.params["name"]}, нажми "Поиск", '
                                                             'чтобы найти анкеты', keyboard=keyboard.get_keyboard())
                    else:
                        self.message_send(event.user_id, 'Ошибка получения данных', keyboard=keyboard.get_keyboard())

                elif event.text.lower() == 'поиск':
                    """Логика для поиска анкет"""
                    self.message_send(
                        event.user_id, 'Начинаем поиск', keyboard=keyboard.get_keyboard())
                    if self.worksheets:
                        worksheet = self.worksheets.pop()
                        photos = self.vk_tools.get_photos(worksheet['id'])
                        photo_string = ''
                        for photo in photos:
                            photo_string += f'photo{photo["owner_id"]}_{photo["id"]},'
                    else:
                        self.worksheets = self.vk_tools.search_worksheet(self.params, self.offset)
                        worksheet = self.worksheets.pop()
                        self.offset += 50

                    """проверка анкеты в бд в соответствии с event.user_id"""
                    while self.data_base.check_user(event.user_id, worksheet["id"]) is True:
                        worksheet = self.worksheets.pop()

                    """добавление анкеты в бд в  соответствии с event.user_id"""
                    if self.data_base.check_user(event.user_id, worksheet["id"]) is False:
                        self.data_base.add_user(event.user_id, worksheet["id"])

                        photos = self.vk_tools.get_photos(worksheet['id'])
                        photo_string = ''
                        for photo in photos:
                            photo_string += f'photo{photo["owner_id"]}_{photo["id"]},'

                        self.message_send(
                            event.user_id,
                            f'Имя: {worksheet["name"]}. Страница: vk.com/id{worksheet["id"]}',
                            attachment=photo_string, keyboard=keyboard.get_keyboard()
                        )

                elif event.text.lower() == 'пока':
                    self.message_send(
                        event.user_id, 'До новых встреч', keyboard=keyboard.get_keyboard())
                else:
                    self.message_send(
                        event.user_id, 'Неизвестная команда', keyboard=keyboard.get_keyboard())

    def chat_keyboard(self, buttons, button_colors):
        keyboard: VkKeyboard = VkKeyboard(one_time=True)
        for button, button_color in zip(buttons, button_colors):
            keyboard.add_button(button, button_color)
        return keyboard


if __name__ == '__main__':
    bot_interface = BotInterface(community_token, access_token)
    bot_interface.event_handler()
