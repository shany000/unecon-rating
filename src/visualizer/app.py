import streamlit as st

st.set_page_config(page_title="UNEcon Rating", layout="wide")


def home() -> None:
    st.title("UNEcon Rating")
    st.write(
        "Аналитика успеваемости студентов Санкт-Петербургского государственного "
        "экономического университета. Выберите режим сравнения в меню слева."
    )

    left, right = st.columns(2)
    with left:
        st.subheader("Сравнение студентов")
        st.write(
            "Сравнение средней оценки и баллов двух студентов по семестрам и предметам."
        )
        st.page_link(
            students_page,
            label="Открыть сравнение студентов",
        )

    with right:
        st.subheader("Сравнение групп")
        st.write(
            "Сравнение средних оценок и баллов двух групп по общим предметам и семестрам."
        )
        st.page_link(
            groups_page,
            label="Открыть сравнение групп",
        )

    st.divider()
    st.caption(
        "Для первого запуска каталог загружается автоматически при старте Docker Compose."
    )


home_page = st.Page(home, title="Главная", default=True)
students_page = st.Page(
    "pages/students_comparison.py",
    title="Сравнение студентов",
)
groups_page = st.Page(
    "pages/groups_comparison.py",
    title="Сравнение групп",
)

navigation = st.navigation(
    [
        home_page,
        students_page,
        groups_page,
    ]
)
navigation.run()
