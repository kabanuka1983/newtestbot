from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton


async def start_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True)
    markup.row(KeyboardButton(text='Подтвердите телефон', request_contact=True))
    return markup


async def quantity_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.row(InlineKeyboardButton(text='+', callback_data=f'plus'),
               InlineKeyboardButton(text='-', callback_data=f'minus'))
    markup.row(InlineKeyboardButton(text='✅Подтвердить', callback_data=f'periods'))
    markup.row(InlineKeyboardButton(text='⬅Назад', callback_data='cancel'))
    return markup


async def menu_keyboard():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.row(InlineKeyboardButton(text='Вступить в клуб', callback_data='registration'))
    markup.row(InlineKeyboardButton(text='Проверить подписку клуба', callback_data='info'))
    # markup.row(InlineKeyboardButton(text='Продлить подписку клуба', callback_data='donat'))
    return markup


async def menu_keyboard2():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.row(InlineKeyboardButton(text='Проверить подписку клуба', callback_data='info'))
    markup.row(InlineKeyboardButton(text='Продлить подписку клуба', callback_data='pay'))
    return markup


async def menu_exit_keyboard():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.row(InlineKeyboardButton(text='☰Меню',
                                    callback_data='menu'))
    return markup


async def approval_keyboard():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.row(InlineKeyboardButton(text='✅Подтвердить',
                                    callback_data='approve'))
    markup.row(InlineKeyboardButton(text='⬅Назад',
                                    callback_data='cancel'))
    return markup


async def back_keyboard():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.row(InlineKeyboardButton(text='⬅Назад',
                                    callback_data='cancel'))
    return markup


# async def admin_start_keyboard():
#     markup = InlineKeyboardMarkup(row_width=1)
#     markup.row(InlineKeyboardButton(text='Панель администратора',
#                                     callback_data='admin_panel'))
#     markup.row(InlineKeyboardButton(text='Меню блюд',
#                                     callback_data='dish_menu'))
#     markup.row(InlineKeyboardButton(text='Инфо',
#                                     callback_data='info'))
#     return markup
#
#
# async def admin_panel_keyboard():
#     markup = InlineKeyboardMarkup(row_width=1)
#     markup.row(InlineKeyboardButton(text='Внести изменения в меню',
#                                     callback_data='db_mutation'))
#     markup.row(InlineKeyboardButton(text='Зачислить оплату',
#                                     callback_data='credit_mutation'))
#     markup.row(InlineKeyboardButton(text='⬅Назад',
#                                     callback_data='cancel'))
#     return markup
#
#
# async def base_change_keyboard(db_dishes):
#     markup = InlineKeyboardMarkup(row_width=1)
#     for dish in db_dishes:
#         text_button = f'{dish.name}: {dish.price} грн.'
#         markup.insert(InlineKeyboardButton(text=text_button, callback_data=f'mutation{dish.name}'))
#     markup.row(InlineKeyboardButton(text='Добавить блюдо в меню', callback_data='new_item'))
#     markup.row(InlineKeyboardButton(text='⬅Назад', callback_data='cancel'))
#     return markup
#
#
# async def mutation_keyboard():
#     markup = InlineKeyboardMarkup(row_width=1)
#     markup.row(InlineKeyboardButton(text='Изменить наименование', callback_data='name'))
#     markup.row(InlineKeyboardButton(text='Изменить цену', callback_data='price'))
#     markup.row(InlineKeyboardButton(text='Удалить', callback_data='delete'))
#     markup.row(InlineKeyboardButton(text='⬅Назад', callback_data='cancel'))
#     return markup
#
#
# async def credit_mutation_abc_keyboard(customers: dict):
#     markup = InlineKeyboardMarkup(row_width=2)
#     for l in sorted(list(customers.keys())):
#         markup.insert(InlineKeyboardButton(text=l, callback_data=f'letter{l}'))
#     markup.row(InlineKeyboardButton(text='⬅Назад', callback_data='cancel'))
#     return markup
#
#
# async def credit_names_keyboard(customers: dict):
#     markup = InlineKeyboardMarkup(row_width=1)
#     for k, v in customers.items():
#         markup.insert(InlineKeyboardButton(text=v.pseudonym, callback_data=f'push{v.pseudonym}'))
#     markup.row(InlineKeyboardButton(text='⬅Назад', callback_data='cancel'))
#     return markup


async def cancel_keyboard():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.row(InlineKeyboardButton(text='⬅Назад', callback_data='cancel'))
    return markup

