from __future__ import annotations

import streamlit as st
from dotenv import load_dotenv

from analyzer import AnalyzerService
from core import CoreService
from database import Neo4jDatabase
from parser.service import ParserService
from visualizer.charts import (
    average_grade_chart,
    average_points_chart,
    semester_subject_points_chart,
)


load_dotenv()


st.set_page_config(
    page_title="UNEcon Rating",
    layout="wide",
)


@st.cache_resource
def get_core() -> CoreService:
    parser = ParserService()
    database = Neo4jDatabase()
    analyzer = AnalyzerService()

    database.verify_connectivity()

    return CoreService(
        parser=parser,
        database=database,
        analyzer=analyzer,
    )


core = get_core()


st.title("UNEcon Rating")

st.header("Сравнение студентов")


years = core.get_years()

if not years:
    st.warning(
        "Каталог ещё не загружен в базу данных."
    )

    if st.button(
        "Загрузить каталог",
    ):
        with st.spinner(
            "Загрузка каталога..."
        ):
            core.initialize_catalog()

        st.rerun()

    st.stop()


year = st.selectbox(
    "Год поступления",
    years,
)


directions = core.get_directions(
    year,
)

if not directions:
    st.warning(
        "Для выбранного года "
        "направления не найдены."
    )

    st.stop()


direction = st.selectbox(
    "Направление",
    directions,
    format_func=lambda item: item.name,
)


groups = core.get_groups(
    year,
    direction.id,
)

if not groups:
    st.warning(
        "Для выбранного направления "
        "группы не найдены."
    )

    st.stop()


group = st.selectbox(
    "Группа",
    groups,
    format_func=lambda item: item.name,
)


students = core.get_students(
    group.id,
)

if len(students) < 2:
    st.warning(
        "В группе недостаточно студентов "
        "для сравнения."
    )

    st.stop()


student_1 = st.selectbox(
    "Первый студент",
    students,
    format_func=lambda item: (
        f"{item.name} ({item.id})"
    ),
    key="student_1",
)


student_2_options = [
    student
    for student in students
    if student.id != student_1.id
]


student_2 = st.selectbox(
    "Второй студент",
    student_2_options,
    format_func=lambda item: (
        f"{item.name} ({item.id})"
    ),
    key="student_2",
)


if st.button(
    "Сравнить студентов",
    type="primary",
):
    with st.spinner(
        "Получение данных и анализ..."
    ):
        comparison = core.compare_students(
            student_1.id,
            student_2.id,
        )

    st.session_state[
        "comparison"
    ] = comparison

    st.session_state[
        "comparison_student_1"
    ] = student_1

    st.session_state[
        "comparison_student_2"
    ] = student_2


if "comparison" not in st.session_state:
    st.info(
        "Выберите двух студентов "
        "и нажмите «Сравнить студентов»."
    )

    st.stop()


comparison = st.session_state[
    "comparison"
]

comparison_student_1 = st.session_state[
    "comparison_student_1"
]

comparison_student_2 = st.session_state[
    "comparison_student_2"
]


st.divider()

st.header("Общая успеваемость")


col1, col2 = st.columns(2)


with col1:
    st.subheader(
        comparison_student_1.name
    )

    st.metric(
        "Средняя оценка",
        (
            f"{comparison.student_1_overall_average_grade:.2f}"
            if comparison.student_1_overall_average_grade
            is not None
            else "Нет данных"
        ),
    )

    st.metric(
        "Средние баллы",
        (
            f"{comparison.student_1_overall_average_points:.2f}"
            if comparison.student_1_overall_average_points
            is not None
            else "Нет данных"
        ),
    )


with col2:
    st.subheader(
        comparison_student_2.name
    )

    st.metric(
        "Средняя оценка",
        (
            f"{comparison.student_2_overall_average_grade:.2f}"
            if comparison.student_2_overall_average_grade
            is not None
            else "Нет данных"
        ),
    )

    st.metric(
        "Средние баллы",
        (
            f"{comparison.student_2_overall_average_points:.2f}"
            if comparison.student_2_overall_average_points
            is not None
            else "Нет данных"
        ),
    )


st.divider()

st.header("Успеваемость по семестрам")


st.plotly_chart(
    average_grade_chart(
        comparison,
        comparison_student_1.name,
        comparison_student_2.name,
    ),
    width="stretch",
)


st.plotly_chart(
    average_points_chart(
        comparison,
        comparison_student_1.name,
        comparison_student_2.name,
    ),
    width="stretch",
)


st.divider()

st.header("Детализация по семестрам")


for semester in comparison.semesters:
    with st.expander(
        f"Семестр {semester.semester}"
    ):
        st.write(
            f"Общих предметов: "
            f"{semester.common_subjects_count}"
        )

        col1, col2 = st.columns(2)

        with col1:
            st.subheader(
                comparison_student_1.name
            )

            st.metric(
                "Средняя оценка",
                (
                    f"{semester.student_1_average_grade:.2f}"
                    if semester.student_1_average_grade
                    is not None
                    else "Нет данных"
                ),
            )

            st.metric(
                "Средние баллы",
                (
                    f"{semester.student_1_average_points:.2f}"
                    if semester.student_1_average_points
                    is not None
                    else "Нет данных"
                ),
            )

        with col2:
            st.subheader(
                comparison_student_2.name
            )

            st.metric(
                "Средняя оценка",
                (
                    f"{semester.student_2_average_grade:.2f}"
                    if semester.student_2_average_grade
                    is not None
                    else "Нет данных"
                ),
            )

            st.metric(
                "Средние баллы",
                (
                    f"{semester.student_2_average_points:.2f}"
                    if semester.student_2_average_points
                    is not None
                    else "Нет данных"
                ),
            )

        st.plotly_chart(
            semester_subject_points_chart(
                semester,
                comparison_student_1.name,
                comparison_student_2.name,
            ),
            width="stretch",
        )