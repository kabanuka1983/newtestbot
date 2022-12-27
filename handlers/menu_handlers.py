from datetime import datetime, tzinfo
from typing import Union

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove, LabeledPrice, PreCheckoutQuery

from data.config import BIG_TEXT, PERIOD
from keyboard.inline.choice_buttons import start_keyboard, menu_keyboard, approval_keyboard, menu_exit_keyboard, \
    menu_keyboard2, back_keyboard, quantity_keyboard
from loader import dp
from utils import database, states
from utils.database import Customer

db = database.DBCommands()


@dp.message_handler(Command('start', prefixes='/'))
@dp.message_handler(Command('start', prefixes='/'), state='*')
async def start_phone_request(message: Message, state: FSMContext):
    current_data: dict = await state.get_data()
    user_id = message.from_user.id
    customer = await db.get_customer(user_id)
    if customer:
        if customer.subs_check:
            await states.MainMenu.full_reg.set()
            return await main_menu(call=message, state=state)
        else:
            await states.MainMenu.half_reg.set()
            return await main_menu(call=message, state=state)
    else:
        markup = await start_keyboard()
        current_message = await message.answer(text='Подтвердите номер телефона', reply_markup=markup)
        current_data.update({'message': current_message})
        await state.set_data(current_data)


@dp.message_handler(content_types=types.ContentType.CONTACT)
@dp.message_handler(content_types=types.ContentType.CONTACT, state='*')
async def registration_phone(message: Message, state: FSMContext):
    current_data: dict = await state.get_data()
    # text = BIG_TEXT
    date = datetime.now().timestamp()

    if message.from_user.id == message.contact.user_id:
        new_customer = await db.add_new_customer(message=message, date=date)
    else:
        await message.delete()
        return 

    if new_customer:
        is_msg = current_data.get('message')
        if is_msg:
            await current_data['message'].delete()

        # markup = await menu_keyboard()
        # current_message = await message.answer(text=text, reply_markup=markup, parse_mode='HTML')
        # await message.delete()
        # current_data.update({'message': current_message})
        # await state.set_data(current_data)
        await states.MainMenu.half_reg.set()
        return await main_menu(call=message, state=state)
    else:
        old_customer: Customer = await db.get_customer(message.from_user.id)

        if old_customer.subs_check:
            await states.MainMenu.full_reg.set()
            await main_menu(call=message, state=state)
        else:
            # await registration_start(call=message, state=state)
            await states.MainMenu.half_reg.set()
            return await main_menu(call=message, state=state)


@dp.callback_query_handler(text_contains='registration', state='*')
# @dp.message_handler(Command(['registration'], prefixes=['/']), state='*')
async def registration_start(call: Union[CallbackQuery, Message], state: FSMContext):
    current_data: dict = await state.get_data()
    # user_id = call.from_user.id
    # customer = await db.get_customer(user_id)
    text = 'Как тебя зовут? (Пример: Владимир Зеленский)'
    if isinstance(call, CallbackQuery):
        await dp.bot.answer_callback_query(call.id)
        current_message = await call.message.edit_text(text=text)
    else:
        current_message = await call.answer(text=text)
        await call.delete()

    current_data.update({'message': current_message})
    await state.set_data(current_data)
    await states.RegMenu.reg_name.set()
    # if customer:
    #     if isinstance(call, CallbackQuery):
    #         await dp.bot.answer_callback_query(call.id)
    #         current_message = await call.message.edit_text(text=text)
    #     elif isinstance(call, Message):
    #         current_message = await call.answer(text=text)
    #         await call.delete()
    #
    #     current_data.update({'message': current_message})
    #     await state.set_data(current_data)
    #     await states.RegMenu.reg_name.set()
    # else:
    #     await start_phone_request(message=call, state=state)


@dp.message_handler(regexp=r"^([А-Я,а-я-Ёё]+ [А-Я,а-я-Ёё]+)$", state=[states.RegMenu.reg_name])
async def registration_name(message: Message, state: FSMContext):
    current_data: dict = await state.get_data()
    # await delete_messages(state=state)
    name = message.text.lower()
    current_data.update({'name': name})
    text = 'Сколько лет? (Пример: 47)'

    await message.delete()
    current_message = await current_data['message'].edit_text(text=text)
    current_data.update({'message': current_message})
    await state.set_data(current_data)
    current_state = await state.get_state()  # del
    if current_state == 'RegMenu:reg_name':  # del
        await states.RegMenu.reg_age.set()
    # else:
    #     await states.ChangePseudonym.surname.set()


@dp.message_handler(regexp=r"^([0-9]+)$", state=[states.RegMenu.reg_age])
async def registration_age(message: Message, state: FSMContext):
    current_data: dict = await state.get_data()
    # await delete_messages(state=state)
    age = int(message.text)
    current_data.update({'age': age})
    text = 'С какого вы города?(Пример: Киев)'

    await message.delete()
    current_message = await current_data['message'].edit_text(text=text)
    current_data.update({'message': current_message})
    await state.set_data(current_data)
    current_state = await state.get_state()  # del
    if current_state == 'RegMenu:reg_age':   # def
        await states.RegMenu.reg_location.set()
    # else:
    #     await states.ChangePseudonym.surname.set()


@dp.message_handler(regexp=r"^([А-Я,а-я-Ёё]+)$", state=[states.RegMenu.reg_location])
async def registration_location(message: Message, state: FSMContext):
    current_data: dict = await state.get_data()
    # await delete_messages(state=state)
    location = message.text.lower()
    current_data.update({'location': location})
    current_data.update({'customer_id': message.from_user.id})  # delete
    text = f'Все верно?\n\nИмя:{current_data["name"].title()}\n\nВозраст:{current_data["age"]}\n\nГород:{current_data["location"].capitalize()}'
    markup = await approval_keyboard()

    await message.delete()
    current_message = await current_data['message'].edit_text(text=text, reply_markup=markup)

    current_data.update({'message': current_message})
    await state.set_data(current_data)
    
    current_state = await state.get_state()      # todo delete
    if current_state == 'RegMenu:reg_location':  # todo delete
        # await state.reset_state()
        await states.RegMenu.reg_approve.set()
    # else:
    #     await states.ChangePseudonym.surname.set()


@dp.callback_query_handler(text_contains='approve', state=[states.RegMenu.reg_approve])
async def registration_fin(call: CallbackQuery, state: FSMContext):
    await dp.bot.answer_callback_query(call.id)

    current_data: dict = await state.get_data()
    name = current_data['name']
    age = current_data['age']
    location = current_data['location']
    customer_id = current_data['customer_id']  # customer_id = call.from_user.id

    await db.update_fin_registration(customer_id=customer_id,
                                     pseudonym=name,
                                     age=age,
                                     location=location)

    await get_invoice(call=call, state=state)


@dp.callback_query_handler(text_contains='pay', state='*')
async def invoice_form(call: CallbackQuery, state: FSMContext):
    await dp.bot.answer_callback_query(call.id)
    current_data: dict = await state.get_data()
    periods = 1
    current_data.update({'periods': periods})
    markup = await quantity_keyboard()
    text = 'Какой период подписки желаете оплатить:' \
           f'<b>{periods*30} дней</b>'

    await call.message.edit_text(text=text, reply_markup=markup)

    await state.set_data(current_data)


@dp.callback_query_handler(text_contains='plus', state='*')
async def period_plus(call: CallbackQuery, state: FSMContext):
    await dp.bot.answer_callback_query(call.id)
    current_data: dict = await state.get_data()
    periods = current_data.get('periods')
    max_periods = 3

    if periods == max_periods or periods is None:
        return
    else:
        periods += 1

    current_data.update({'periods': periods})
    text = 'Какой период подписки желаете оплатить:' \
           f'<b>{periods*30} дней</b>'

    markup = await quantity_keyboard()

    await call.message.edit_text(text=text, reply_markup=markup)

    await state.set_data(current_data)


@dp.callback_query_handler(text_contains='minus', state='*')
async def period_minus(call: CallbackQuery, state: FSMContext):
    await dp.bot.answer_callback_query(call.id)
    current_data: dict = await state.get_data()
    periods = current_data.get('periods')
    max_periods = 3

    if periods == 1 or periods is None:
        return
    else:
        periods -= 1

    current_data.update({'periods': periods})
    text = 'Какой период подписки желаете оплатить:' \
           f'<b>{periods*30} дней</b>'

    markup = await quantity_keyboard()

    await call.message.edit_text(text=text, reply_markup=markup)

    await state.set_data(current_data)


@dp.callback_query_handler(text_contains='periods', state='*')
async def periods_approve(call: CallbackQuery, state: FSMContext):
    await dp.bot.answer_callback_query(call.id)
    await get_invoice(call=call, state=state)


async def get_invoice(call: CallbackQuery, state: FSMContext):
    await dp.bot.answer_callback_query(call.id)
    current_data: dict = await state.get_data()

    periods = current_data.get('periods')
    if periods is None:
        periods = 1
    amount = 5000
    text = 'Внеси членский взнос ✍🏼\n(карта для оплаты: 4444 3333 2222 1111):'
    current_message = await call.message.edit_text(text=text)
    current_data.update({'message': current_message})

    prices = [LabeledPrice(label=f'Подписка на {periods*30} дней', amount=amount*periods)]
    provider_token = '1661751239:TEST:5610452833'

    invoice = await dp.bot.send_invoice(chat_id=call.message.chat.id,
                                        title='Подписка',
                                        description='Оплата членства в клубе',
                                        payload=str(periods),
                                        provider_token=provider_token,
                                        currency='uah',
                                        prices=prices,
                                        start_parameter='subs-example')

    current_data.update({'invoice': invoice})
    await state.set_data(current_data)


@dp.pre_checkout_query_handler(lambda query: True, state='*')
async def checkout(pre_checkout_query: PreCheckoutQuery):
    await dp.bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True,
                                           error_message="Что-то пошло не так")


@dp.message_handler(content_types=['successful_payment'], state='*')  # aiogram.utils.exceptions.InvalidQueryID: Query is too old and response timeout expired or query id is invalid
async def got_payment(message: Message, state: FSMContext):
    print(message)
    await delete_messages(state)
    current_data: dict = await state.get_data()
    customer_id = message.from_user.id
    timestamp_now = int(datetime.now().timestamp())
    total_amount = message.successful_payment.total_amount
    currency = message.successful_payment.currency
    payload = message.successful_payment.invoice_payload
    period = PERIOD
    periods = int(payload)
    customer = await db.get_customer(customer_id=customer_id)
    markup = await menu_exit_keyboard()

    if timestamp_now > customer.subs_before:
        subs_before = timestamp_now + period * periods  # ?periods

        await db.update_subs_before(customer_id=customer_id, subs_before=subs_before)
        current_message = await dp.bot.send_message(chat_id=message.chat.id,
                                                    text='Поздравляю, ты в клубе 🧑🏻‍💻',
                                                    parse_mode='Markdown',
                                                    reply_markup=markup)
    else:
        subs_before = customer.subs_before + period * periods
        print_date = datetime.fromtimestamp(subs_before).strftime("%d-%m-%Y")

        await db.update_subs_before(customer_id=customer_id, subs_before=subs_before)
        current_message = await dp.bot.send_message(chat_id=message.chat.id,
                                                    text=f'Подписка продлена до <b>{print_date}</b> 🧑🏻‍💻',
                                                    parse_mode='HTML',
                                                    reply_markup=markup)

    current_data.update({'message': current_message})
    await state.set_data(current_data)


@dp.message_handler(Command(['menu'], prefixes='/'), state='*')
@dp.callback_query_handler(text_contains='menu', state='*')
async def main_menu(call: Union[CallbackQuery, Message], state: FSMContext):
    if isinstance(call, CallbackQuery):
        await dp.bot.answer_callback_query(call.id)
    current_data: dict = await state.get_data()
    current_state = await state.get_state()
    print(current_state)
    text = BIG_TEXT

    if current_state == 'MainMenu:full_reg':
        markup = await menu_keyboard2()
    elif current_state == 'MainMenu:half_reg':
        markup = await menu_keyboard()
    else:
        return await start_phone_request(message=call, state=state)

    if isinstance(call, CallbackQuery):
        current_message = await call.message.edit_text(text=text, reply_markup=markup, parse_mode='HTML')
    else:
        current_message = await call.answer(text=text, reply_markup=markup, parse_mode='HTML')  # if subs_check
        await call.delete()
        await delete_messages(state=state)

    current_data.update({'message': current_message})
    await state.set_data(current_data)


@dp.callback_query_handler(text_contains='info', state='*')
async def info(call: CallbackQuery, state: FSMContext):
    await dp.bot.answer_callback_query(call.id)
    current_data: dict = await state.get_data()

    customer = await db.get_customer(call.from_user.id)
    markup = await back_keyboard()

    if customer:
        if customer.subs_check:
            await states.MainMenu.full_reg.set()
            datetime_db = datetime.fromtimestamp(customer.subs_before)
            if datetime_db > datetime.now():
                customer_subs_date = datetime_db.strftime('%d-%m-%Y')
                text = f'Текущая подписка до <b>{customer_subs_date}</b>'
            else:
                text = f'К сожалению не удалось подтвердить ваше участие в клубе.\nВнесите членский взнос 🧑🏻‍💻'
        else:
            await states.MainMenu.half_reg.set()
            text = f'К сожалению не удалось подтвердить ваше участие в клубе.\n\nЗавершите регистрацию и\nВнесите членский взнос 🧑🏻‍💻'
    else:
        await states.MainMenu.no_reg.set()
        text = f'Зарегистрируйся'

    current_message = await call.message.edit_text(text=text, reply_markup=markup, parse_mode='HTML')

    current_data.update({'message': current_message})
    await state.set_data(current_data)

# async def pre_registration(message: Message):
#     print(message)
#     date = datetime.now().timestamp()
#     await db.add_new_customer(message=message, date=date)


# @dp.message_handler(Command('start', prefixes='/'))
# async def registration_start(message: Message, state: FSMContext):
#     old_customer = await db.get_customer(message.from_user.id)
#     if old_customer:
#         return
#     await states.RegMenu.reg_name.set()
#     await registration_name(message=message, state=state)
#
#
# async def registration_name(message: Union[Message, CallbackQuery], state):
#     order: dict = await state.get_data()
#     text = 'Введи имя'
#     if isinstance(message, Message):
#         order_message = await message.answer(text=text)
#     elif isinstance(message, CallbackQuery):
#         order_message = await message.message.edit_text(text=text)
#     order.update({'order_message': [order_message]})
#     await state.set_data(order)
#
#
# @dp.message_handler(regexp=r"^([А-Я,а-я-Ёё]+)$", state=[states.RegMenu.reg_name, states.ChangePseudonym.name])
# async def registration(message: Message, state: FSMContext):
#     order: dict = await state.get_data()
#     await delete_messages(state=state)
#     name = message.text
#     order.update({'name': name})
#     text = 'Введи фамилию'
#     order_message = await message.answer(text=text)
#     order.update({'order_message': [order_message]})
#     await state.set_data(order)
#     current_state = await state.get_state()
#     if current_state == 'RegMenu:reg_name':
#         await states.RegMenu.reg_surname.set()
#     else:
#         await states.ChangePseudonym.surname.set()


# @dp.message_handler(regexp=r"^([А-Я,а-я-Ёё]+)$", state=[states.RegMenu.reg_surname, states.ChangePseudonym.surname])
# async def registration_fin(message: Message, state: FSMContext):
#     order: dict = await state.get_data()
#     surname: str = message.text
#     name: str = order.pop('name')
#     date = datetime.now().date()
#     date_str = date.strftime('%d %m %Y')
#     pseudonym = f'{surname.capitalize()} {name.capitalize()}'
#     await delete_messages(state=state)
#     customer = message.from_user
#     current_state = await state.get_state()
#
#     if current_state == 'RegMenu:reg_surname':
#         await db.add_new_customer(customer=customer, customer_pseudonym=pseudonym)
#     else:
#         old_customer: Customer = await db.get_customer(customer.id)
#         menu_date = await db.get_menu_date()
#         menu_is_instance = date == menu_date
#         if old_customer:
#             if menu_is_instance:
#                 try:
#                     update_worksheet_pseudonym(old_pseudonym=old_customer.pseudonym, new_pseudonym=pseudonym, date=date_str)
#                 except WorksheetNotFound:
#                     pass
#             await db.update_pseudonym(customer=old_customer, pseudonym=pseudonym)
#         else:
#             return
#     text = f'Вы зарегистрировались под именем:\n\n{pseudonym}'
#     await message.answer(text=text, disable_notification=True)
#     await state.reset_state()


# @dp.message_handler(state=[states.RegMenu.reg_name, states.RegMenu.reg_surname,
#                            states.ChangePseudonym.name, states.ChangePseudonym.surname])
# async def wrong(message: Message, state: FSMContext):
#     current_state = await state.get_state()
#     order: dict = await state.get_data()
#     name = 'фамилию'
#     if current_state == 'RegMenu:reg_name' or current_state == 'ChangePseudonym:name':
#         name = 'имя'
#     text = f'Не верный формат ввода, попробуй ещё раз ввести {name} кириллицей без пробелов'
#     order_message = await message.answer(text=text)
#     order.update({'order_message': [order_message]})
#     await state.set_data(order)
#     await message.delete()
#
#
# @dp.message_handler(Command(['menu', 'еню'], prefixes=['/', 'М']), state='*')
# @dp.throttled(rate=2)
# async def menu_command(message: types.Message, state: FSMContext):
#     old_customer = await db.get_customer(message.from_user.id)
#     if old_customer:
#         await delete_messages(state=state)
#         await state.reset_state()
#         await start_choice(message, state)
#         await message.delete()
#     else:
#         await registration_start(message=message, state=state)
#         await message.delete()
#
#
# async def start_choice(message: Union[CallbackQuery, Message], state: FSMContext):
#     await states.Order.main.set()
#     markup = await start_keyboard()
#     order: dict = await state.get_data()
#     text = '"Меню блюд"-для выбора блюд\n "Инфо"-для просмотра команд'
#     if message.from_user.id == int(ADMIN_ID):
#         markup = await admin_start_keyboard()
#         text = '"Панель администратора"-для входа в панель администратора\n ' \
#                '"Меню блюд"-для выбора блюд\n "Инфо"-для просмотра команд'
#     if isinstance(message, Message):
#         order_message = await message.answer(text=text, reply_markup=markup, disable_notification=True)
#     if isinstance(message, CallbackQuery):
#         await bot.answer_callback_query(message.id)
#         order_message = await message.message.edit_text(text=text, reply_markup=markup)
#     order.update({'order_message': [order_message]})
#     await state.set_data(order)
#
#
# @dp.callback_query_handler(text_contains='info', state=states.Order.main)
# async def info(call: CallbackQuery, state=FSMContext):
#     await bot.answer_callback_query(call.id)
#     markup = await cancel_keyboard()
#     data: dict = await state.get_data()
#     await states.Order.info.set()
#
#     text = '/change_reg_name'
#     order_message = await call.message.edit_text(text=text, reply_markup=markup)
#
#     data.update({'order_message': [order_message]})
#     await state.set_data(data)
#
#
# @dp.callback_query_handler(text_contains='dish_menu', state=states.Order.dishes_dict)
# @dp.callback_query_handler(text_contains='dish_menu', state=states.Order.main)
# async def dishes_choice(call: CallbackQuery, state: FSMContext):
#     await bot.answer_callback_query(call.id)
#
#     menu_date = await db.get_menu_date()
#     date = datetime.now().date()
#     menu_is_instance = date == menu_date
#
#     if menu_is_instance:
#         order: dict = await state.get_data()
#         db_dishes = await db.get_dishes()
#         mutate_message = order.pop('order_message', None)
#         if mutate_message:
#             try:
#                 await mutate_message[0].delete()
#             except:
#                 pass
#
#         try:
#             await call.message.delete()
#         except:
#             pass
#         for dish in db_dishes:
#             markup = await dishes_menu_keyboard(dish_id=dish.id)
#             order_dish = order.get(dish.id)
#             quantity = None
#             if order_dish:
#                 quantity = order_dish[1]
#             if quantity:
#                 text_item = f'{dish.name}: {dish.price}грн. ✅ x {quantity}'
#             else:
#                 text_item = f'{dish.name}: {dish.price} грн.'
#             menu_message = await call.message.answer(text=text_item, reply_markup=markup, disable_notification=True)
#             order.update({dish.id: [menu_message, quantity, dish.price, dish.name]})
#
#         order_string = ''
#         total = 0
#         for k, v in order.items():
#             quantity = v[1]
#             if quantity:
#                 dish = get_dish_from_list_by_id(db_dishes=db_dishes, dish_id=k)
#                 order_string += f'{v[3]} {dish.price}x{quantity}: {dish.price * quantity}грн.\n'
#                 total += dish.price * quantity
#         text = f'Ваш выбор \n\n{order_string}\nИтоговая стоимость {total} грн.'
#         markup1 = await approval_keyboard()
#         order_message = await call.message.answer(text=text, reply_markup=markup1, disable_notification=True)
#         order.update({'order_message': [order_message]})
#
#         await state.set_data(order)
#         await states.Order.dishes_dict.set()
#     else:
#         markup = await cancel_keyboard()
#         text = f'Меню на <b>{date.strftime("%d.%m.%Y")}</b> еще <b>не готово</b>, попробуйте немного позже'
#         await call.message.edit_text(text=text, reply_markup=markup, parse_mode='HTML')
#         await states.Order.dishes_dict.set()
#
#
# @dp.callback_query_handler(text_contains='plus', state=states.Order.dishes_dict)
# async def plus(call: CallbackQuery, state: FSMContext):
#     await bot.answer_callback_query(call.id)
#     call_dish = int(call.data[4:])
#     markup = await dishes_menu_keyboard(call_dish)
#     order: dict = await state.get_data()
#     call_list = order.get(call_dish)
#     call_quantity = call_list[1]
#     call_price = call_list[2]
#     if call_quantity:
#         call_quantity += 1
#     else:
#         call_quantity = 1
#     text_item = f'{call_list[3]}: {call_price}грн. ✅ x {call_quantity}'
#     call_list[1] = call_quantity
#     order.update({call_dish: call_list})
#     await call.message.edit_text(text=text_item, reply_markup=markup)
#     await state.set_data(order)
#     await mutate_order_message(state=state)
#
#
# @dp.callback_query_handler(text_contains='minus', state=states.Order.dishes_dict)
# async def minus(call: CallbackQuery, state: FSMContext):
#     await bot.answer_callback_query(call.id)
#     call_dish = int(call.data[5:])
#     markup = await dishes_menu_keyboard(call_dish)
#     order: dict = await state.get_data()
#     call_list = order.get(call_dish)
#     call_quantity = call_list[1]
#     call_price = call_list[2]
#     if call_quantity and call_quantity > 1:
#         call_quantity -= 1
#         text_item = f'{call_list[3]}: {call_price}грн. ✅ x {call_quantity}'
#     elif call_quantity is None or call_quantity <= 1:
#         call_quantity = 0
#         text_item = f'{call_list[3]}: {call_price}грн.'
#     call_list[1] = call_quantity
#     order.update({call_dish: call_list})
#     await call.message.edit_text(text=text_item, reply_markup=markup)
#     await state.set_data(order)
#     await mutate_order_message(state=state)
#
#
# async def mutate_order_message(state: FSMContext):
#     order: dict = await state.get_data()
#     mutate_message = order.pop('order_message')
#     order_string = ''
#     total = 0
#     for _, v in order.items():
#         quantity = v[1]
#         if quantity:
#             price = v[2]
#             dish_name = v[3]
#             order_string += f'{dish_name} {price}x{quantity}: {price * quantity}грн.\n'
#             total += price * quantity
#     text = f'Ваш выбор \n\n{order_string}\nИтоговая стоимость {total} грн.'
#     markup1 = await approval_keyboard()
#     await mutate_message[0].edit_text(text=text, reply_markup=markup1)
#
#
# # @dp.callback_query_handler(text_contains='approve', state=states.Order.dishes_dict)
# # async def approve(call: CallbackQuery, state: FSMContext):
# #     await bot.answer_callback_query(call.id)
# #     db_dishes = await db.get_dishes()
# #     customer = await db.get_customer(call.from_user.id)
# #     date: str = datetime.now().date().strftime('%d %m %Y')
# #     order: dict = await state.get_data()
# #     mutate_message = order.pop('order_message')
# #     markup = await approval_keyboard_reverse()
# #
# #     order_string = ''
# #     total = 0
# #     for k, v in order.items():
# #         quantity = v[1]
# #         if quantity:
# #             dish_name = v[3]
# #             dish = get_dish_from_list_by_id(db_dishes=db_dishes, dish_id=k)
# #             order_string += f'{dish_name} {dish.price}x{quantity}: {dish.price * quantity}грн.\n'
# #             total += dish.price * quantity
# #         message = v[0]
# #         await message.delete()
# #     text = f'Ваш выбор \n\n{order_string}\nИтоговая стоимость {total} грн.'
# #     if customer.current_order == 1:
# #         current_order_dict = get_order_from_sheet(pseudonym=customer.pseudonym, date=date, dishes=db_dishes)
# #         current_order_string = ''
# #         current_total = 0
# #         for d, q in current_order_dict.items():
# #             if q:
# #                 dish = get_dish_from_list_by_name(db_dishes=db_dishes, dish=d)
# #                 current_order_string += f'{d} {dish.price}x{q}: {dish.price * q}грн.\n'
# #                 current_total += dish.price * q
# #         text = f'Вы уже сделали заказ сегодня\nПодтвердите, чтобы отменить текущий заказ и принять новый\n❌\n' \
# #                f'{current_order_string}Итоговая стоимость {current_total} грн.\n\n✅\n'+text
# #     # todo pygsheets.exceptions.WorksheetNotFound
# #     await mutate_message[0].edit_text(text=text, reply_markup=markup)
# #     await states.Order.checkout.set()
#
#
# # @dp.callback_query_handler(text_contains='checkout', state=states.Order.checkout)
# # async def fin_approve(call: CallbackQuery, state: FSMContext):
# #     await bot.answer_callback_query(call.id)
# #     date: str = datetime.now().date().strftime('%d %m %Y')
# #     dishes = await db.get_dishes()
# #     order: dict = await state.get_data()
# #     customer = await db.get_customer(call.from_user.id)
# #     if customer.current_order == 1:
# #         credit_back = cancel_order(pseudonym=customer.pseudonym, date=date, dishes=dishes)
# #         await db.credit_up(customer_id=customer.customer_id, val=credit_back)
# #     credit = add_order_to_sheet(customer=customer, date=date, order=order, dishes=dishes)
# #     await db.credit_down(customer_id=customer.customer_id, val=credit)
# #     await db.set_current_order(customer=customer)
# #
# #     await state.reset_state()
# #     text = call.message.text
# #     await call.message.edit_text(text=text)
#
#
# @dp.message_handler(Command(['change_reg_name'], prefixes='/'), state='*')
# async def change_pseudonym(message: Message, state: FSMContext):
#     await delete_messages(state=state)
#     customer: Customer = await db.get_customer(message.from_user.id)
#     if customer:
#         markup = await approval_keyboard()
#         text = f'Ты обнаружил ошибку в имени:\n{customer.pseudonym} ?\nЖелаешь изменить его?'
#         await states.ChangePseudonym.initial.set()
#         await message.delete()
#         await message.answer(text=text, reply_markup=markup)
#     else:
#         await states.RegMenu.reg_name.set()
#         await registration_name(message=message, state=state)
#
#
# @dp.callback_query_handler(text_contains='approve', state=states.ChangePseudonym.initial)
# async def to_reregistration(call: CallbackQuery, state=FSMContext):
#     await states.ChangePseudonym.name.set()
#     await registration_name(message=call, state=state)
#
#
@dp.callback_query_handler(text_contains='cancel', state='*')
@dp.throttled(rate=0.5)
async def cancel(call: Union[CallbackQuery, Message], state: FSMContext):
    current_state = await state.get_state()
    if current_state == 'RegMenu:reg_approve':
        await state.reset_state()
        return await registration_start(call=call, state=state)
    if current_state == 'MainMenu:full_reg':
        return await main_menu(call=call, state=state)
    if current_state == 'MainMenu:half_reg':
        return await main_menu(call=call, state=state)
    if current_state == 'MainMenu:no_reg':
        return await main_menu(call=call, state=state)
#     if current_state == 'AdminMenu:change' or current_state == 'AdminMenu:rollback':
#         await state.reset_state()
#         return await admin_panel(call=call, state=state)
#     if current_state == 'AdminMenu:panel' or current_state == 'Order:info':
#         await state.reset_state()
#         return await start_choice(message=call, state=state)
#     if current_state == 'AdminMenu:credit':
#         await state.reset_state()
#         return await admin_panel(call=call, state=state)
#     if current_state == 'AdminMenu:credit_push':
#         await state.reset_state()
#         return await credit_mutation_abc(call=call, state=state)
#     if current_state == 'AdminMenu:credit_upd':
#         await state.reset_state()
#         return await credit_mutation_abc(call=call, state=state)
#     if current_state == 'AdminMenu:instance_menu':
#         await state.reset_state()
#         return await admin_panel(call=call, state=state)
#     if current_state == 'ChangePseudonym:initial':
#         await state.reset_state()
#         await call.message.delete()
#         return
#     if not current_state:
#         return await start_choice(message=call, state=state)


async def delete_messages(state):
    current_data: dict = await state.get_data()
    message = current_data.get('message')

    try:
        await message.delete()
    except:
        pass

    invoice = current_data.pop('invoice', None)
    if invoice:
        try:
            await invoice.delete()
        except:
            pass


@dp.message_handler()
@dp.message_handler(state='*')
async def terminator(message):
    try:
        await message.delete()
    except:
        pass


#
# def get_dish_from_list_by_id(db_dishes, dish_id):
#     for d in db_dishes:
#         if d.id == dish_id:
#             return d
#
#
# def get_dish_from_list_by_name(db_dishes, dish):
#     for d in db_dishes:
#         if d.name == dish:
#             return d
#
#
# # todo aiogram.utils.exceptions.MessageNotModified
# # todo raise WorksheetNotFound
