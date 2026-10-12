import streamlit as st

from visualizer.charts import (
    average_grade_chart,
    average_points_chart,
    semester_subject_points_chart,
)
from visualizer.common import (
    compare_students_cached,
    format_number,
    get_core,
    render_student_card,
)

st.title("Сравнение студентов")

core = get_core()
years = core.get_years()
if not years:
    st.warning("Каталог пока не загружен.")
    if st.button("Загрузить каталог"):
        with st.spinner("Загружаем каталог и сохраняем его в Neo4j..."):
            core.initialize_catalog()
        st.rerun()

first_col, second_col = st.columns(2)
with first_col:
    first = render_student_card(core, "Первый студент", "student_1")
with second_col:
    second = render_student_card(core, "Второй студент", "student_2")

first_id = first["student"].id if first else None
second_id = second["student"].id if second else None
same_student = first_id is not None and first_id == second_id
if same_student:
    st.warning("Выберите двух разных студентов.")

if st.button(
    "Сравнить студентов",
    type="primary",
    disabled=first is None or second is None or same_student,
):
    with st.spinner("Получаем данные студентов и рассчитываем сравнение..."):
        comparison = compare_students_cached(first_id, second_id)
    st.session_state["student_comparison"] = comparison
    st.session_state["student_comparison_ids"] = (first_id, second_id)

current_ids = (first_id, second_id)
comparison = st.session_state.get("student_comparison")
comparison_ids = st.session_state.get("student_comparison_ids")
if comparison is None or comparison_ids != current_ids:
    st.info("Выберите студентов и нажмите «Сравнить студентов».")
    st.stop()

first_name = first["student"].name
second_name = second["student"].name

st.divider()
st.header("Результаты")
meta_1, meta_2 = st.columns(2)
with meta_1:
    st.subheader(first_name)
    st.caption(f"{first['year']} · {first['direction_name']} · {first['group_name']}")
with meta_2:
    st.subheader(second_name)
    st.caption(f"{second['year']} · {second['direction_name']} · {second['group_name']}")

metric_group_1, metric_group_2 = st.columns(2)
with metric_group_1:
    st.markdown(f"**{first_name}**")
    grade_col, points_col = st.columns(2)
    grade_col.metric(
        "Средняя оценка",
        format_number(comparison.student_1_overall_average_grade),
    )
    points_col.metric(
        "Средний балл",
        format_number(comparison.student_1_overall_average_points),
    )
with metric_group_2:
    st.markdown(f"**{second_name}**")
    grade_col, points_col = st.columns(2)
    grade_col.metric(
        "Средняя оценка",
        format_number(comparison.student_2_overall_average_grade),
    )
    points_col.metric(
        "Средний балл",
        format_number(comparison.student_2_overall_average_points),
    )

if not comparison.semesters:
    st.info("Не найдено общих семестров для сравнения.")
else:
    grade_col, points_col = st.columns(2)
    with grade_col:
        st.plotly_chart(
            average_grade_chart(comparison, first_name, second_name),
            use_container_width=True,
        )
    with points_col:
        st.plotly_chart(
            average_points_chart(comparison, first_name, second_name),
            use_container_width=True,
        )

    for semester in comparison.semesters:
        with st.expander(f"Семестр {semester.semester}", expanded=True):
            st.write(f"Общих предметов: {semester.common_subjects_count}")
            student_1_col, student_2_col = st.columns(2)
            with student_1_col:
                st.markdown(f"**{first_name}**")
                grade_col, points_col = st.columns(2)
                grade_col.metric(
                    "Средняя оценка",
                    format_number(semester.student_1_average_grade),
                )
                points_col.metric(
                    "Средний балл",
                    format_number(semester.student_1_average_points),
                )
            with student_2_col:
                st.markdown(f"**{second_name}**")
                grade_col, points_col = st.columns(2)
                grade_col.metric(
                    "Средняя оценка",
                    format_number(semester.student_2_average_grade),
                )
                points_col.metric(
                    "Средний балл",
                    format_number(semester.student_2_average_points),
                )

            if semester.common_subjects:
                st.plotly_chart(
                    semester_subject_points_chart(semester, first_name, second_name),
                    use_container_width=True,
                )
            else:
                st.info("Нет общих предметов в этом семестре.")
