from __future__ import annotations

import plotly.graph_objects as go

from models import SemesterComparison, StudentComparison


def average_grade_chart(
    comparison: StudentComparison,
    student_1_name: str,
    student_2_name: str,
) -> go.Figure:
    semesters = [
        item.semester
        for item in comparison.semesters
    ]

    student_1_values = [
        item.student_1_average_grade
        for item in comparison.semesters
    ]

    student_2_values = [
        item.student_2_average_grade
        for item in comparison.semesters
    ]

    figure = go.Figure()

    figure.add_trace(
        go.Scatter(
            x=semesters,
            y=student_1_values,
            mode="lines+markers",
            name=student_1_name,
        )
    )

    figure.add_trace(
        go.Scatter(
            x=semesters,
            y=student_2_values,
            mode="lines+markers",
            name=student_2_name,
        )
    )

    figure.update_layout(
        title="Средняя оценка по семестрам",
        xaxis_title="Семестр",
        yaxis_title="Средняя оценка",
        yaxis=dict(
            range=[0, 5],
        ),
        hovermode="x unified",
    )

    return figure


def average_points_chart(
    comparison: StudentComparison,
    student_1_name: str,
    student_2_name: str,
) -> go.Figure:
    semesters = [
        item.semester
        for item in comparison.semesters
    ]

    student_1_values = [
        item.student_1_average_points
        for item in comparison.semesters
    ]

    student_2_values = [
        item.student_2_average_points
        for item in comparison.semesters
    ]

    figure = go.Figure()

    figure.add_trace(
        go.Scatter(
            x=semesters,
            y=student_1_values,
            mode="lines+markers",
            name=student_1_name,
        )
    )

    figure.add_trace(
        go.Scatter(
            x=semesters,
            y=student_2_values,
            mode="lines+markers",
            name=student_2_name,
        )
    )

    figure.update_layout(
        title="Средние баллы по семестрам",
        xaxis_title="Семестр",
        yaxis_title="Средние баллы",
        hovermode="x unified",
    )

    return figure


def semester_subject_points_chart(
    semester: SemesterComparison,
    student_1_name: str,
    student_2_name: str,
) -> go.Figure:
    subjects = semester.common_subjects

    student_1_values = [
        semester.student_1_points_by_subject.get(
            subject
        )
        for subject in subjects
    ]

    student_2_values = [
        semester.student_2_points_by_subject.get(
            subject
        )
        for subject in subjects
    ]

    figure = go.Figure()

    figure.add_trace(
        go.Bar(
            x=subjects,
            y=student_1_values,
            name=student_1_name,
        )
    )

    figure.add_trace(
        go.Bar(
            x=subjects,
            y=student_2_values,
            name=student_2_name,
        )
    )

    figure.update_layout(
        title=(
            f"Баллы по предметам — "
            f"{semester.semester} семестр"
        ),
        xaxis_title="Предмет",
        yaxis_title="Баллы",
        barmode="group",
        xaxis=dict(
            tickangle=-45,
            automargin=True,
        ),
        yaxis=dict(
            range=[0, 100],
        ),
        height=500,
    )

    return figure