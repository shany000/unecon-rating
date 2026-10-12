from __future__ import annotations

from dotenv import load_dotenv
import streamlit as st

from analyzer import AnalyzerService
from core import CoreService
from database import Neo4jDatabase
from models import Direction, Group, StudentRef
from parser.service import ParserService

CACHE_TTL_SECONDS = 6 * 60 * 60


@st.cache_resource
def get_core() -> CoreService:
    load_dotenv()
    parser = ParserService()
    database = Neo4jDatabase()
    database.verify_connectivity()
    return CoreService(
        parser=parser,
        database=database,
        analyzer=AnalyzerService(),
    )


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def compare_students_cached(
    first_student_id: int,
    second_student_id: int,
):
    return get_core().compare_students(first_student_id, second_student_id)


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def compare_groups_cached(
    first_group_id: str,
    second_group_id: str,
    first_group_name: str,
    second_group_name: str,
    _progress_callback=None,
):
    return get_core().compare_groups(
        first_group_id=first_group_id,
        second_group_id=second_group_id,
        first_group_name=first_group_name,
        second_group_name=second_group_name,
        progress_callback=_progress_callback,
    )


def _save_selection(widget_key: str, saved_key: str) -> None:
    st.session_state[saved_key] = st.session_state[widget_key]


def _persistent_selectbox(
    label: str,
    options: list,
    key: str,
    format_func=None,
):
    saved_key = f"_saved_{key}"
    saved_value = st.session_state.get(saved_key)
    index = 0
    if saved_value is not None:
        saved_id = getattr(saved_value, "id", None)
        if saved_id is not None:
            for option_index, option in enumerate(options):
                if getattr(option, "id", None) == saved_id:
                    index = option_index
                    break
        else:
            try:
                index = options.index(saved_value)
            except ValueError:
                index = 0

    selected = st.selectbox(
        label,
        options=options,
        index=index,
        format_func=format_func or str,
        key=key,
        on_change=_save_selection,
        args=(key, saved_key),
    )
    st.session_state[saved_key] = selected
    return selected


def render_student_card(core: CoreService, title: str, key_prefix: str) -> dict | None:
    st.subheader(title)

    years = core.get_years()
    if not years:
        st.info("Каталог пока не загружен.")
        return None

    year = _persistent_selectbox(
        "Год поступления",
        options=years,
        key=f"{key_prefix}_year",
    )
    directions: list[Direction] = core.get_directions(year)
    if not directions:
        st.warning("Для выбранного года направления не найдены.")
        return None

    direction = _persistent_selectbox(
        "Направление",
        options=directions,
        format_func=lambda item: item.name,
        key=f"{key_prefix}_direction",
    )
    groups: list[Group] = core.get_groups(year, direction.id)
    if not groups:
        st.warning("Для выбранного направления группы не найдены.")
        return None

    group = _persistent_selectbox(
        "Группа",
        options=groups,
        format_func=lambda item: item.name,
        key=f"{key_prefix}_group",
    )
    students: list[StudentRef] = core.get_students(group.id)
    if not students:
        st.warning("В выбранной группе не найдены студенты.")
        return None

    student = _persistent_selectbox(
        "Студент",
        options=students,
        format_func=lambda item: item.name,
        key=f"{key_prefix}_student",
    )

    return {
        "year": year,
        "direction_name": direction.name,
        "group_id": group.id,
        "group_name": group.name,
        "student": student,
    }


def render_group_card(core: CoreService, title: str, key_prefix: str) -> dict | None:
    st.subheader(title)

    years = core.get_years()
    if not years:
        st.info("Каталог пока не загружен.")
        return None

    year = _persistent_selectbox(
        "Год поступления",
        options=years,
        key=f"{key_prefix}_year",
    )
    directions = core.get_directions(year)
    if not directions:
        st.warning("Для выбранного года направления не найдены.")
        return None

    direction = _persistent_selectbox(
        "Направление",
        options=directions,
        format_func=lambda item: item.name,
        key=f"{key_prefix}_direction",
    )
    groups = core.get_groups(year, direction.id)
    if not groups:
        st.warning("Для выбранного направления группы не найдены.")
        return None

    group = _persistent_selectbox(
        "Группа",
        options=groups,
        format_func=lambda item: item.name,
        key=f"{key_prefix}_group",
    )

    return {
        "year": year,
        "direction_name": direction.name,
        "group_id": group.id,
        "group_name": group.name,
    }


def format_number(value: float | None, digits: int = 2) -> str:
    if value is None:
        return "Нет данных"
    return f"{value:.{digits}f}"
