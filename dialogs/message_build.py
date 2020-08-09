from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
)

from .utils import _edit_sep

import math
from pandas import DataFrame


def build_eval_buttons(
    options: list, user_id: int = 0, message_id: int = 0
) -> list:
    ajusted_cb_data = []
    if options:
        for text, cb_data in options:
            new_cb_data = f"confidence_{user_id}_{message_id}_{cb_data}"
            ajusted_cb_data.append((text, new_cb_data))
        return ajusted_cb_data
    else:
        return None


def build_nav_options(
    command_name: str,
    number_of_rows: int,
    index: int = 0,
    message_id: int = 0,
    page_size: int = 1,
    l_index: int = 0,
    list_size: int = 1,
) -> list:

    nav_options = []
    # Adicionar botões de navegação da lista atual
    if number_of_rows > page_size:
        current = index
        prev_index = current - page_size
        next_index = current + page_size

        if current <= 0:
            prev_index = number_of_rows - number_of_rows % page_size
        elif current + page_size >= number_of_rows:
            next_index = 0

        current_page = f"{math.ceil(current/page_size) + 1}/{math.ceil(number_of_rows/page_size)}"

        nav_options.append(
            ("👈", f"{command_name}_{l_index}_{message_id}_{prev_index}")
        )
        nav_options.append((current_page, "this_button_is_decorative"))
        nav_options.append(
            ("👉", f"{command_name}_{l_index}_{message_id}_{next_index}")
        )

    # Se houver mais uma lista de resultados, adicionar botão de navegação de listas
    if list_size > 1:
        prev_list_index = l_index - 1
        next_list_index = l_index + 1

        if prev_list_index < 0:
            prev_list_index = list_size - 1
        if next_list_index >= list_size:
            next_list_index = 0

        nav_options.append(
            ("⏪", f"{command_name}-list_lprev_{message_id}_{prev_list_index}")
        )
        nav_options.append(
            ("🔍 Info", f"details_{command_name}_{message_id}_{l_index}")
        )
        nav_options.append(
            ("⏩", f"{command_name}-list_lnext_{message_id}_{next_list_index}")
        )

    return nav_options


def build_nav_menu(
    label: str, message: str, number_of_rows: int, index: int
) -> InlineKeyboardMarkup:
    reply_markup = None
    if number_of_rows > 0:
        # opções de navegação
        nav_options = build_nav_options(
            label, number_of_rows, message_id=message.message_id, index=index,
        )
        # Construir menu
        reply_markup = build_menu(nav_options, n_cols=3)
    return reply_markup


def build_menu(
    options: list,
    n_cols: int = 2,
    header_options: list = None,
    footer_options: list = None,
) -> InlineKeyboardMarkup:

    # Mapeia o menu de opções para InlineKeyboardButton
    def map_options_on_buttons(i, n_cols):
        return [
            InlineKeyboardButton(text, callback_data=cb_data)
            for text, cb_data in options[i : i + n_cols]
        ]

    keyboard = []

    if options:
        keyboard = [
            map_options_on_buttons(i, n_cols)
            for i in range(0, len(options), n_cols)
        ]

    if header_options:
        options = header_options
        keyboard.insert(0, map_options_on_buttons(0, len(options)))

    if footer_options:
        options = footer_options
        keyboard.append(map_options_on_buttons(0, len(options)))

    if keyboard:
        return InlineKeyboardMarkup(keyboard)
    else:
        return None


def build_reply_keyboard(
    options: list, n_cols: int = 2
) -> ReplyKeyboardMarkup:
    keyboard = [
        options[i : i + n_cols] for i in range(0, len(options), n_cols)
    ]
    return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)


def paginate_data(
    field: str,
    data: list,
    list_index: int = 0,
    list_size: int = 1,
    rating_options: list = None,
    index: int = 0,
    message_id: int = 0,
    **kwargs,
) -> (str, InlineKeyboardMarkup):
    text = ""

    df = data[list_index]

    page_size = kwargs.get("page_size")
    if page_size:
        page_size = int(page_size)
    else:
        page_size = 1

    col_name_pos = kwargs.get("col_name_pos")
    line_sep = _edit_sep(kwargs.get("line_sep"))
    col_sep = _edit_sep(kwargs.get("col_sep"))

    number_format = kwargs.get("number_format")
    if number_format:
        number_format = number_format.replace("\\n", "\n")
        number_format = number_format.replace("\\t", "\t")

    number_of_rows = df.shape[0]
    last = index + page_size

    if last >= number_of_rows:
        last = number_of_rows
    columnsNamesArr = df.columns.values

    # Se nome das colunas colocada antes dos resultados
    if col_name_pos == "top":
        for key in columnsNamesArr:
            text += f"*{key}*{col_sep}"
        text += line_sep

    # Resultados paginados
    for current_index in range(index, last):
        row = df.iloc[
            current_index,
        ]
        if number_format:
            text += f"*{number_format.format(current_index+1)}*"
        for key in columnsNamesArr:
            if col_name_pos == "default":
                text += f"*{key}*: "
            text += f"{row[key]}{col_sep}"
        if current_index <= last - 2:
            text += line_sep

    # Se nome das colunas colocada após os resuktados
    if col_name_pos == "bottom":
        text += line_sep
        for key in columnsNamesArr:
            text += f"*{key}*{col_sep}"

    nav_options = build_nav_options(
        field,
        number_of_rows,
        index,
        message_id=message_id,
        page_size=page_size,
        list_size=list_size,
        l_index=list_index,
    )
    reply_markup = build_menu(
        nav_options, n_cols=3, header_options=rating_options
    )

    return text, reply_markup
