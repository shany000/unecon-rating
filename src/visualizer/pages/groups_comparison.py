import pandas as pd
import streamlit as st

from visualizer.charts import group_semester_average_chart, group_semester_subject_chart
from visualizer.common import format_number, get_core, render_group_card

st.set_page_config(page_title="Сравнение групп", layout="wide")
st.title("Сравнение групп")
st.write(
    "Сравнение средних оценок и баллов по общим предметам в каждом семестре. "
    "В расчётах учитываются оценки всех студентов выбранной группы."
)

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
    first = render_group_card(core, "Первая группа", "group_1")
with second_col:
    second = render_group_card(core, "Вторая группа", "group_2")

first_id = first["group_id"] if first else None
second_id = second["group_id"] if second else None
same_group = first_id is not None and first_id == second_id
if same_group:
    st.warning("Выберите две разные группы.")

if st.button(
    "Сравнить группы",
    type="primary",
    disabled=first is None or second is None or same_group,
):
    progress = st.progress(0, text="Подготавливаем сравнение...")

    def update_progress(done: int, total: int) -> None:
        fraction = done / total if total else 1.0
        progress.progress(
            fraction,
            text=f"Загружено карточек студентов: {done} из {total}",
        )

    try:
        comparison = core.compare_groups(
            first_group_id=first_id,
            second_group_id=second_id,
            first_group_name=first["group_name"],
            second_group_name=second["group_name"],
            progress_callback=update_progress,
        )
        st.session_state["group_comparison"] = comparison
        st.session_state["group_comparison_ids"] = (first_id, second_id)
    except Exception as error:
        st.error(f"Не удалось сравнить группы: {error}")
    finally:
        progress.empty()

comparison = st.session_state.get("group_comparison")
comparison_ids = st.session_state.get("group_comparison_ids")
if comparison is None or comparison_ids != (first_id, second_id):
    st.info("Выберите две группы и нажмите «Сравнить группы».")
    st.stop()

st.divider()
st.header("Результаты")

group_1_col, group_2_col = st.columns(2)
with group_1_col:
    st.subheader(comparison.group_1_name)
    st.caption(f"Студентов в группе: {comparison.group_1_student_count}")
    grade_col, points_col = st.columns(2)
    grade_col.metric(
        "Средняя оценка",
        format_number(comparison.group_1_overall_average_grade),
    )
    points_col.metric(
        "Средний балл",
        format_number(comparison.group_1_overall_average_points),
    )

with group_2_col:
    st.subheader(comparison.group_2_name)
    st.caption(f"Студентов в группе: {comparison.group_2_student_count}")
    grade_col, points_col = st.columns(2)
    grade_col.metric(
        "Средняя оценка",
        format_number(comparison.group_2_overall_average_grade),
    )
    points_col.metric(
        "Средний балл",
        format_number(comparison.group_2_overall_average_points),
    )

st.caption(
    "Общие показатели рассчитаны по всем доступным оценкам группы. "
    "В семестровых графиках по предметам сравниваются средние баллы только "
    "по предметам, которые есть в обеих группах. Таблица показывает количество "
    "учтённых оценок и баллов для каждого предмета."
)

if not comparison.semesters:
    st.info("Не найдено общих семестров с данными для сравнения.")
else:
    grade_col, points_col = st.columns(2)
    with grade_col:
        st.plotly_chart(
            group_semester_average_chart(comparison, "grade"),
            use_container_width=True,
        )
    with points_col:
        st.plotly_chart(
            group_semester_average_chart(comparison, "points"),
            use_container_width=True,
        )

    for semester in comparison.semesters:
        with st.expander(
            f"Семестр {semester.semester} · общих предметов: {len(semester.common_subjects)}",
            expanded=False,
        ):
            semester_group_1, semester_group_2 = st.columns(2)
            with semester_group_1:
                st.markdown(f"**{comparison.group_1_name}**")
                grade_col, points_col = st.columns(2)
                grade_col.metric(
                    "Средняя оценка",
                    format_number(semester.group_1_average_grade),
                )
                points_col.metric(
                    "Средний балл",
                    format_number(semester.group_1_average_points),
                )

            with semester_group_2:
                st.markdown(f"**{comparison.group_2_name}**")
                grade_col, points_col = st.columns(2)
                grade_col.metric(
                    "Средняя оценка",
                    format_number(semester.group_2_average_grade),
                )
                points_col.metric(
                    "Средний балл",
                    format_number(semester.group_2_average_points),
                )

            if not semester.subjects:
                st.info("В этом семестре нет общих предметов.")
                continue

            points_tab, table_tab = st.tabs(
                ["Средние баллы по предметам", "Таблица по предметам"]
            )
            with points_tab:
                st.plotly_chart(
                    group_semester_subject_chart(semester, comparison, "points"),
                    use_container_width=True,
                )
            with table_tab:
                rows = []
                for subject in semester.subjects:
                    rows.append({
                        "Предмет": subject.subject,
                        f"Оценка · {comparison.group_1_name}": subject.group_1_average_grade,
                        f"Количество оценок · {comparison.group_1_name}": subject.group_1_grade_count,
                        f"Оценка · {comparison.group_2_name}": subject.group_2_average_grade,
                        f"Количество оценок · {comparison.group_2_name}": subject.group_2_grade_count,
                        f"Баллы · {comparison.group_1_name}": subject.group_1_average_points,
                        f"Количество баллов · {comparison.group_1_name}": subject.group_1_points_count,
                        f"Баллы · {comparison.group_2_name}": subject.group_2_average_points,
                        f"Количество баллов · {comparison.group_2_name}": subject.group_2_points_count,
                    })
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
