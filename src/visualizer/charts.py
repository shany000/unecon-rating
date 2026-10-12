from __future__ import annotations

import plotly.graph_objects as go

from models import GroupComparison, GroupSemesterComparison, SemesterComparison, StudentComparison


def average_grade_chart(
    comparison: StudentComparison,
    student_1_name: str,
    student_2_name: str,
) -> go.Figure:
    semesters = [item.semester for item in comparison.semesters]
    figure = go.Figure()
    figure.add_trace(go.Scatter(
        x=semesters,
        y=[item.student_1_average_grade for item in comparison.semesters],
        mode="lines+markers",
        name=student_1_name,
    ))
    figure.add_trace(go.Scatter(
        x=semesters,
        y=[item.student_2_average_grade for item in comparison.semesters],
        mode="lines+markers",
        name=student_2_name,
    ))
    figure.update_layout(
        title="Средняя оценка по семестрам",
        xaxis_title="Семестр",
        yaxis_title="Средняя оценка",
        yaxis=dict(range=[0, 5]),
        legend_title="Студент",
    )
    return figure


def average_points_chart(
    comparison: StudentComparison,
    student_1_name: str,
    student_2_name: str,
) -> go.Figure:
    semesters = [item.semester for item in comparison.semesters]
    figure = go.Figure()
    figure.add_trace(go.Scatter(
        x=semesters,
        y=[item.student_1_average_points for item in comparison.semesters],
        mode="lines+markers",
        name=student_1_name,
    ))
    figure.add_trace(go.Scatter(
        x=semesters,
        y=[item.student_2_average_points for item in comparison.semesters],
        mode="lines+markers",
        name=student_2_name,
    ))
    figure.update_layout(
        title="Средний балл по семестрам",
        xaxis_title="Семестр",
        yaxis_title="Средний балл",
        yaxis=dict(range=[0, 100]),
        legend_title="Студент",
    )
    return figure


def semester_subject_points_chart(
    semester: SemesterComparison,
    student_1_name: str,
    student_2_name: str,
) -> go.Figure:
    figure = go.Figure()
    figure.add_trace(go.Bar(
        x=semester.common_subjects,
        y=[semester.student_1_points_by_subject.get(subject) for subject in semester.common_subjects],
        name=student_1_name,
    ))
    figure.add_trace(go.Bar(
        x=semester.common_subjects,
        y=[semester.student_2_points_by_subject.get(subject) for subject in semester.common_subjects],
        name=student_2_name,
    ))
    figure.update_layout(
        title=f"Баллы по предметам — семестр {semester.semester}",
        xaxis_title="Предмет",
        yaxis_title="Баллы",
        yaxis=dict(range=[0, 100]),
        barmode="group",
        height=500,
    )
    figure.update_xaxes(tickangle=-35)
    return figure


def group_semester_average_chart(
    comparison: GroupComparison,
    metric: str,
) -> go.Figure:
    if metric == "grade":
        title = "Средняя оценка по семестрам"
        yaxis_title = "Средняя оценка"
        range_values = [0, 5]
        first_values = [item.group_1_average_grade for item in comparison.semesters]
        second_values = [item.group_2_average_grade for item in comparison.semesters]
    else:
        title = "Средний балл по семестрам"
        yaxis_title = "Средний балл"
        range_values = [0, 100]
        first_values = [item.group_1_average_points for item in comparison.semesters]
        second_values = [item.group_2_average_points for item in comparison.semesters]

    figure = go.Figure()
    figure.add_trace(go.Scatter(
        x=[item.semester for item in comparison.semesters],
        y=first_values,
        mode="lines+markers",
        name=comparison.group_1_name,
    ))
    figure.add_trace(go.Scatter(
        x=[item.semester for item in comparison.semesters],
        y=second_values,
        mode="lines+markers",
        name=comparison.group_2_name,
    ))
    figure.update_layout(
        title=title,
        xaxis_title="Семестр",
        yaxis_title=yaxis_title,
        yaxis=dict(range=range_values),
        legend_title="Группа",
    )
    return figure


def group_semester_subject_chart(
    semester: GroupSemesterComparison,
    comparison: GroupComparison,
    metric: str,
) -> go.Figure:
    if metric == "grade":
        title = f"Средняя оценка по предметам — семестр {semester.semester}"
        yaxis_title = "Средняя оценка"
        range_values = [0, 5]
        first_values = [item.group_1_average_grade for item in semester.subjects]
        second_values = [item.group_2_average_grade for item in semester.subjects]
    else:
        title = f"Средний балл по предметам — семестр {semester.semester}"
        yaxis_title = "Средний балл"
        range_values = [0, 100]
        first_values = [item.group_1_average_points for item in semester.subjects]
        second_values = [item.group_2_average_points for item in semester.subjects]

    figure = go.Figure()
    figure.add_trace(go.Bar(
        x=[item.subject for item in semester.subjects],
        y=first_values,
        name=comparison.group_1_name,
    ))
    figure.add_trace(go.Bar(
        x=[item.subject for item in semester.subjects],
        y=second_values,
        name=comparison.group_2_name,
    ))
    figure.update_layout(
        title=title,
        xaxis_title="Предмет",
        yaxis_title=yaxis_title,
        yaxis=dict(range=range_values),
        barmode="group",
        height=500,
        legend_title="Группа",
    )
    figure.update_xaxes(tickangle=-35)
    return figure
