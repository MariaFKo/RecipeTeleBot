from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from utils import get_category_list, get_meals_by_category, get_meal_recipe
from utils import translate_ru, start_menu, build_keyboard
from utils import MAX_MEALS
from random import sample
import asyncio


router = Router()
category_list = []

# class with states
class MealChoice(StatesGroup):
    selecting_category = State()  # user is choosing a category
    accepting_meal_list = State()  # user has requested recipes

# processes /category_search_random <n>
@router.message(Command("category_search_random"))
async def category_search_random(message: Message, command: types.Message, state: FSMContext):
    # validate argument n
    if command.args is None:
        await message.answer(text=f'Ошибка: необходимо указать количество случайных рецептов для вывода. '
                                  f'Введите команду /category_search_random '
                                  f'и через пробел укажите количество блюд от 1 до {MAX_MEALS}')
        return
    elif (len(command.args) > 1 or
          not str(command.args).isdigit() or
          int(command.args) <= 0 or
          int(command.args) > MAX_MEALS):
        await message.answer(text=f'Ошибка: ожидается параметр в формате целого числа от 1 до {MAX_MEALS}')
        return

    # store recipe count in state
    await state.set_data({'recipe_cnt': int(command.args)})

    await message.answer(f'Вы желаете получить {int(command.args)} вариантов блюд.\n'
                         'Дождитесь, пожалуйста, загрузки списка категорий для выбора.\n Идет поиск...',
                         reply_markup=ReplyKeyboardRemove()
                         )

    # store category list for further verification of input category-commands
    global category_list
    category_list = await get_category_list()
    await message.answer(text='Выберите категорию нажатием кнопки', reply_markup=build_keyboard(category_list, 5))

    # set state "user is choosing a category"
    await state.set_state(MealChoice.selecting_category)


# process chosen category
@router.message(lambda message: message.text in category_list and MealChoice.selecting_category)
async def category_chosen(message: Message, state: FSMContext):

    # save category in state data
    await state.update_data(chosen_category=message.text)
    user_data = await state.get_data()

    await message.answer(f'Вы выбрали категорию {user_data["chosen_category"]}. '
                         f'Подождите, пожалуйста, я загружу для Вас {user_data["recipe_cnt"]} '
                         'вариантов блюд этой категории ...',
                         reply_markup=ReplyKeyboardRemove()
                         )

    # get full meal list
    meal_list = await get_meals_by_category(message.text.lower())

    # build random meal list
    if len(meal_list) <= int(user_data["recipe_cnt"]):
        # number of requested recipes is more that available
        s_message = (f"К моему сожалению, выбор рецептов в категории {user_data['chosen_category']} невелик. "
                     f"Предлагаю взглянуть на полный список: \n {translate_ru(', '.join(meal_list))}")
        await state.update_data(chosen_meals=meal_list)
    else:
        await state.update_data(chosen_meals=sample(meal_list, k=int(user_data["recipe_cnt"])))
        user_data = await state.get_data()
        s_message = f"Как Вам такие блюда:\n{translate_ru(', '.join(user_data['chosen_meals']))}"

    await message.answer(text=s_message,
                         reply_markup=build_keyboard(["Покажи рецепты"])
                         )

    # set state waiting for recipe list acceptance by user
    await state.set_state(MealChoice.accepting_meal_list)


@router.message(MealChoice.accepting_meal_list, F.text.lower() == "покажи рецепты")
async def show_meal_recipes(message: Message, state: FSMContext):
    # request and print meal recipe
    async def print_recipes(a_meal: str, a_message: Message):
        recipe = await get_meal_recipe(a_meal)
        await a_message.answer(translate_ru(recipe))

    user_data = await state.get_data()
    await message.answer(f'Подождите, пожалуйста, я загружаю рецепты блюд ...',
                         reply_markup=ReplyKeyboardRemove()
                         )
    # asynchronously request recipes for selected meals
    cr = []
    i = 0
    while i < len(user_data['chosen_meals']):
        cr.append(print_recipes(user_data['chosen_meals'][i], message))
        i += 1
    await asyncio.gather(*cr)

    # clean state and user_data
    user_data.clear()
    await state.clear()

    # transfer to the main menu
    await start_menu(message, 'Рецепты предоставлены. Если желаете продолжить, введите команду.')
