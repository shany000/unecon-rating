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


def render_student_card(
    title: str,
    key_prefix: str,
):
    with st.container(border=True):
        st.subheader(title)

        year_key = f"{key_prefix}_year"
        direction_key = f"{key_prefix}_direction"
        group_key = f"{key_prefix}_group"
        student_key = f"{key_prefix}_student"

        years = core.get_years()

        if not years:
            st.warning(
                "Годы не найдены."
            )
            return None

        year = st.selectbox(
            "Год поступления",
            years,
            key=year_key,
        )

        directions = core.get_directions(
            year,
        )

        if not directions:
            st.warning(
                "Для выбранного года "
                "направления не найдены."
            )
            return None

        direction = st.selectbox(
            "Направление",
            directions,
            format_func=lambda item: item.name,
            key=direction_key,
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
            return None

        group = st.selectbox(
            "Группа",
            groups,
            format_func=lambda item: item.name,
            key=group_key,
        )

        students = core.get_students(
            group.id,
        )

        if not students:
            st.warning(
                "В выбранной группе "
                "студенты не найдены."
            )
            return None

        student = st.selectbox(
            "Студент",
            students,
            format_func=lambda item: (
                f"{item.name} ({item.id})"
            ),
            key=student_key,
        )

        return {
            "year": year,
            "direction": direction,
            "group": group,
            "student": student,
        }


st.title("UNEcon Rating")

st.header("Сравнение студентов")


if not core.get_years():
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


left_col, center_col, right_col = st.columns(
    [10, 1, 10]
)


with left_col:
    first_student = render_student_card(
        "Студент 1",
        "student_1",
    )


with center_col:
    st.markdown(
        "<div style='height: 230px;'></div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div style='text-align: center; "
        "font-size: 28px; font-weight: 700;'>"
        "VS"
        "</div>",
        unsafe_allow_html=True,
    )


with right_col:
    second_student = render_student_card(
        "Студент 2",
        "student_2",
    )


student_1 = (
    first_student["student"]
    if first_student is not None
    else None
)

student_2 = (
    second_student["student"]
    if second_student is not None
    else None
)


if (
    student_1 is not None
    and student_2 is not None
    and student_1.id == student_2.id
):
    st.warning(
        "Нельзя сравнить студента с самим собой. "
        "Выберите разных студентов."
    )

    student_1 = None
    student_2 = None


current_selection = (
    student_1.id if student_1 is not None else None,
    student_2.id if student_2 is not None else None,
)


if (
    "comparison_selection"
    in st.session_state
    and st.session_state[
        "comparison_selection"
    ] != current_selection
):
    st.session_state.pop(
        "comparison",
        None,
    )

    st.session_state.pop(
        "comparison_student_1",
        None,
    )

    st.session_state.pop(
        "comparison_student_2",
        None,
    )

    st.session_state.pop(
        "comparison_info_1",
        None,
    )

    st.session_state.pop(
        "comparison_info_2",
        None,
    )

    st.session_state.pop(
        "comparison_selection",
        None,
    )


st.write("")


compare_col1, compare_col2, compare_col3 = st.columns(
    [1, 2, 1]
)


with compare_col2:
    compare_clicked = st.button(
        "Сравнить студентов",
        type="primary",
        use_container_width=True,
        disabled=(
            student_1 is None
            or student_2 is None
        ),
    )


if compare_clicked:
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

    st.session_state[
        "comparison_info_1"
    ] = {
        "year": first_student["year"],
        "direction": first_student[
            "direction"
        ].name,
        "group": first_student[
            "group"
        ].name,
    }

    st.session_state[
        "comparison_info_2"
    ] = {
        "year": second_student["year"],
        "direction": second_student[
            "direction"
        ].name,
        "group": second_student[
            "group"
        ].name,
    }

    st.session_state[
        "comparison_selection"
    ] = current_selection


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

comparison_info_1 = st.session_state[
    "comparison_info_1"
]

comparison_info_2 = st.session_state[
    "comparison_info_2"
]


st.divider()

st.header("Выбранные студенты")


left_col, center_col, right_col = st.columns(
    [10, 1, 10]
)


with left_col:
    with st.container(border=True):
        st.subheader(
            comparison_student_1.name
        )

        st.write(
            f"**Год:** "
            f"{comparison_info_1['year']}"
        )

        st.write(
            f"**Направление:** "
            f"{comparison_info_1['direction']}"
        )

        st.write(
            f"**Группа:** "
            f"{comparison_info_1['group']}"
        )


with center_col:
    st.markdown(
        "<div style='height: 40px;'></div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div style='text-align: center; "
        "font-size: 24px; font-weight: 700;'>"
        "VS"
        "</div>",
        unsafe_allow_html=True,
    )


with right_col:
    with st.container(border=True):
        st.subheader(
            comparison_student_2.name
        )

        st.write(
            f"**Год:** "
            f"{comparison_info_2['year']}"
        )

        st.write(
            f"**Направление:** "
            f"{comparison_info_2['direction']}"
        )

        st.write(
            f"**Группа:** "
            f"{comparison_info_2['group']}"
        )


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