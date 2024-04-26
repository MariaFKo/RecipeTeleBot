import aiohttp
from aiogram import types
from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from googletrans import Translator
from token_data import OPEN_RECIPE

# maximum of recipies to be provided
MAX_MEALS = 5


# build the keyboard
def build_keyboard(items: list, buttons_perrow = 0) -> ReplyKeyboardMarkup:

    kb = ReplyKeyboardBuilder()
    for item in items:
        kb.add(types.KeyboardButton(text=item))
    if buttons_perrow > 0:
        kb.adjust(buttons_perrow)
    return kb.as_markup(resize_keyboard=True, input_field_placeholder="Выберите категорию")


# build main menu
async def start_menu(message, text):
    #kb = [[types.KeyboardButton(text="Команды"), types.KeyboardButton(text="Описание бота")]]
    #keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Введите команду")
    await message.answer(text, reply_markup=build_keyboard(["Команды", "Описание бота"]))


# переводит на русский язык
def translate_ru(a_string: str) -> str:
    translator = Translator()
    string = translator.translate(a_string, dest='ru')
    return string.text


# возвращает список категорий
async def get_category_list() -> list:
    async with aiohttp.ClientSession() as session:
        async with session.get(url='https://www.themealdb.com/api/json/v1/1/list.php?c=list'
                                   f'&limit=1&appid={OPEN_RECIPE}', ) as resp:
            data = await resp.json()

    category_list = []
    for item in data['meals']:
        category_list.append(item['strCategory'])
    return category_list


# возвращает список блюд для выбранной категории
async def get_meals_by_category(selected_category: str) -> list:
    async with aiohttp.ClientSession() as session:
        async with session.get(url=f'https://www.themealdb.com/api/json/v1/1/filter.php?c={selected_category}'
                                   f'&limit=1&appid={OPEN_RECIPE}', ) as resp:
            data = await resp.json()
    meal_list = []
    for item in data["meals"]:
        meal_list.append(item['strMeal'])
    return meal_list


# возвращает рецепт блюда и ингредиенты
async def get_meal_recipe(meal_name: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url=f'https://www.themealdb.com/api/json/v1/1/search.php?s={meal_name}'
                                   f'&limit=1&appid={OPEN_RECIPE}', ) as resp:
            data = await resp.json()

    ingredients_list = []
    for i in range(19):
        if data['meals'][0]['strIngredient' + str(i + 1)] == '':
            break
        else:
            ingredients_list.append(data['meals'][0]['strIngredient' + str(i + 1)])

    recipe = (f"{meal_name}\n \nРецепт:\n{data['meals'][0]['strInstructions']}\n\nИнгредиенты:\n"
              f"{', '.join(ingredients_list)}")

    return recipe
