import logging

from aiogram.types import ParseMode
from aiogram.utils.markdown import hitalic, hbold

from keyboards import gender_keyboard, request_contact_kb, home_keyboard
from aiogram.dispatcher import FSMContext
from aiogram import types
from states import Profile
from database import db
import strings

log = logging.getLogger(__name__)


async def cmd_start(message: types.Message, state: FSMContext):
    user_exists = db.user_exists(message.from_user.id)
    if user_exists and db.is_user_active(message.from_user.id):
        await message.answer(hbold('Приветствую❗Рад, что вы вернулись!🤗'),
                             parse_mode=ParseMode.HTML, reply_markup=home_keyboard())
        return

    if not user_exists:
        db.add_user(message.from_user.id, message.from_user.full_name, message.from_user.username, message.from_user.language_code)
        if message.get_args():
            user_id = message.get_args()
            if db.user_exists(user_id):
                await state.update_data(inviter=user_id)
    # Set state
    await Profile.name.set()
    await message.answer(strings.welcome_msg(), parse_mode=ParseMode.HTML)
    await message.answer(hitalic("Представьтесь, как вас зовут?"), parse_mode=ParseMode.HTML)


async def process_invalid_name(message: types.Message):
    await message.delete()
    await message.answer(hbold('Имя не должно превышать 25 символов, попробуйте ещё разок!'), parse_mode=ParseMode.HTML)


async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text

    await Profile.next()
    await message.answer(hitalic("Сколько вам лет?"), parse_mode=ParseMode.HTML)


async def process_age_invalid(message: types.Message):
    return await message.reply(hbold("Возраст должен состоять только из цифр. Отправьте корректный возраст!"),
                               parse_mode=ParseMode.HTML)


async def process_age(message: types.Message, state: FSMContext):
    await Profile.next()
    await state.update_data(age=int(message.text))

    await message.answer(hitalic("Кто вы?"), reply_markup=gender_keyboard(strings.MALE, strings.FEMALE),
                         parse_mode=ParseMode.HTML)


async def process_gender_invalid(message: types.Message):
    return await message.delete()


async def process_gender(query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['gender'] = query.data
        await Profile.next()
        await query.message.edit_text(hitalic('Ваш город (Кириллицей)'), parse_mode=ParseMode.HTML)


async def process_city_invalid(message: types.Message):
    await message.answer(hbold('Название города должно быть на кириллице! Попробуйте ещё.'), parse_mode=ParseMode.HTML)


async def process_city(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['city'] = str(message.text).capitalize()
        await Profile.next()
        await message.answer(hitalic('Ваш род занятий (специальность, увлечение)?'), parse_mode=ParseMode.HTML)


async def process_occupation(message: types.Message, state: FSMContext):
    await state.update_data(occupation=message.text)
    await Profile.next()
    await message.answer(hitalic('Опишите себя одним предложением.'), parse_mode=ParseMode.HTML)


async def process_about(message: types.Message, state: FSMContext):
    await state.update_data(about=message.text)
    await Profile.next()
    await message.answer(hitalic('Отправьте свой контакт.'), parse_mode=ParseMode.HTML, reply_markup=request_contact_kb())


async def process_invalid_contact(message: types.Message):
    await message.answer(hbold('Это не ваш контакт, используйте кнопку, чтобы отправить'), parse_mode=ParseMode.HTML)


async def process_contact(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['contact'] = message.contact.phone_number
        await Profile.next()
        await message.answer(hitalic('Пришлите своё фото.'), parse_mode=ParseMode.HTML, reply_markup=types.ReplyKeyboardRemove())


async def process_invalid_photo(message: types.Message):
    await message.answer(hbold('Отправьте мне валидное фото.'), parse_mode=ParseMode.HTML)


async def process_photo_and_save_data(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['photo'] = message.photo[-1].file_id
        city_id = db.get_city_id(data['city'])
        db.update_user_data(message.from_user.id, data['name'], data['age'], data['gender'], city_id,
                            data['occupation'], data['about'], data['photo'], data['contact'])

        if 'inviter' in data.keys():
            increase_by = 10
            log.info(f"{data['inviter']} invited referral")
            if not int(data['gender']):
                increase_by += 40
                log.info("It's a girl :)")
            increased_hearts = db.get_user_hearts(data['inviter']) + increase_by
            db.update_user_hearts(data['inviter'], increased_hearts)
    await state.finish()
    await message.answer(hbold('Отлично!👌 Можете приступать к поиску своей второй половинки!😍 Удачи в любовных делах!✌'),
                         parse_mode=ParseMode.HTML, reply_markup=home_keyboard())
