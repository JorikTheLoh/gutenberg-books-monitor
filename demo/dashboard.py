import streamlit as st
import psycopg2
import pandas as pd

# Настройка страницы (вкладка браузера)
st.set_page_config(page_title="Мониторинг книг", layout="wide")

# Заголовок
st.title("📚 Мониторинг топ-100 книг Project Gutenberg")

# Подключение к базе данных
@st.cache_resource
def init_connection():
    return psycopg2.connect(
        host="localhost",
        database="books_monitor",
        user="postgres",
        password="123"
    )

conn = init_connection()

# Загрузка данных из PostgreSQL
@st.cache_data(ttl=60)  # кеш на 60 секунд
def load_data():
    query = "SELECT title, rank, collected_date FROM books ORDER BY collected_date DESC, rank ASC LIMIT 100"
    return pd.read_sql(query, conn)

df = load_data()

# Показываем последние 10 книг
st.subheader("📖 Текущий топ-10 книг")
latest_date = df['collected_date'].max()
top10 = df[df['collected_date'] == latest_date].head(10)
st.dataframe(top10, use_container_width=True)

# Блок с фильтрами в боковой панели
st.sidebar.header("🔍 Фильтры")

# Фильтр по дате
dates = df['collected_date'].unique()
selected_date = st.sidebar.selectbox("Выберите дату:", sorted(dates, reverse=True))

# Фильтр по поиску
search_term = st.sidebar.text_input("Поиск по названию:")

# Отфильтрованные данные
filtered_df = df[df['collected_date'] == selected_date]
if search_term:
    filtered_df = filtered_df[filtered_df['title'].str.contains(search_term, case=False, na=False)]

st.subheader(f"📋 Книги за {selected_date}")
st.dataframe(filtered_df, use_container_width=True)

# Простая статистика
st.subheader("📊 Статистика")
col1, col2, col3 = st.columns(3)
col1.metric("Всего книг в базе", len(df['title'].unique()))
col2.metric("Записей в истории", len(df))
col3.metric("Последнее обновление", str(latest_date))

# Кнопка для экспорта в CSV
if st.button("📥 Экспортировать в CSV"):
    filtered_df.to_csv("export_books.csv", index=False)
    st.success("Файл export_books.csv сохранён в папке с проектом!")

# --- График динамики книги ---
st.subheader("📈 Динамика позиции книги по дням")

# Получаем список книг для выбора
cursor = conn.cursor()
cursor.execute("SELECT DISTINCT title FROM books ORDER BY title")
books_list = [row[0] for row in cursor.fetchall()]

selected_book = st.selectbox("Выберите книгу:", books_list)

if selected_book:
    # Получаем историю позиций этой книги
    query = """
        SELECT collected_date, rank 
        FROM books 
        WHERE title = %s 
        ORDER BY collected_date ASC
    """
    df_book = pd.read_sql(query, conn, params=[selected_book])
    
    if not df_book.empty:
        st.line_chart(df_book.set_index("collected_date")["rank"])
        st.caption("📌 Чем выше линия, тем хуже позиция (1 — самое лучшее место)")
    else:
        st.info("По этой книге пока нет данных")
