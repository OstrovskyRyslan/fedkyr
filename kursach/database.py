import pyodbc
from tkinter import messagebox


class DatabaseManager:
    """Клас для керування підключенням та операціями з базою даних."""

    def __init__(self):
        try:
            self.conn = pyodbc.connect(
                'DRIVER={ODBC Driver 17 for SQL Server};'
                'SERVER=DESKTOP-QQAOEK4;'
                'DATABASE=EventNotifierApp;'
                'Trusted_Connection=yes;'
                'Encrypt=yes;'
                'TrustServerCertificate=yes;'
            )
            self.cursor = self.conn.cursor()
            self.create_tables()
        except pyodbc.Error as e:
            messagebox.showerror("Помилка підключення", f"Не вдалося підключитись до бази даних:\n{str(e)}")
            raise SystemExit()

    def create_tables(self):
        """Створює таблиці в базі даних, якщо їх ще немає."""
        queries = [
            '''IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='users' AND xtype='U')
               CREATE TABLE users (
                   id INT PRIMARY KEY IDENTITY(1,1),
                   name NVARCHAR(255),
                   email NVARCHAR(100),
                   phone NVARCHAR(20),
                   contact_method NVARCHAR(20)
               )''',
            '''IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='messages' AND xtype='U')
               CREATE TABLE messages (
                   id INT PRIMARY KEY IDENTITY(1,1),
                   [user_id] INT,
                   message NVARCHAR(1000),
                   FOREIGN KEY ([user_id]) REFERENCES users(id) ON DELETE CASCADE
               )''',
            '''IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='events' AND xtype='U')
               CREATE TABLE events (
                   id INT PRIMARY KEY IDENTITY(1,1),
                   [user_id] INT,
                   [event_name] NVARCHAR(255),
                   event_date DATETIME,
                   FOREIGN KEY ([user_id]) REFERENCES users(id) ON DELETE CASCADE
               )'''
        ]

        try:
            with self.conn.cursor() as cursor:
                for query in queries:
                    cursor.execute(query)
            self.conn.commit()
        except pyodbc.Error as e:
            messagebox.showerror("Помилка БД", f"Не вдалося створити таблиці:\n{e}")

    def execute_query(self, query, params=(), fetch=False):
        """Виконує SQL-запит до бази даних.
        Параметри:
        - query: SQL-запит у вигляді рядка
        - params: кортеж параметрів для запиту
        - fetch: якщо True, повертає результати запиту
        """
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, params)
                if fetch:
                    return cursor.fetchall()
                self.conn.commit()
        except pyodbc.Error as e:
            messagebox.showerror("Помилка БД", f"Помилка виконання запиту:\n{e}")

    def close_connection(self):
        """Закриває з'єднання з базою даних."""
        self.conn.close()

    # ДОДАНО: Методи для роботи з подіями
    def add_event(self, user_id, event_name, event_date):
        """Додає подію до бази даних."""
        self.execute_query(
            "INSERT INTO events ([user_id], [event_name], event_date) VALUES (?, ?, ?)",
            (int(user_id), str(event_name), event_date)
        )

    def get_events(self):
        """Отримує всі події."""
        return self.execute_query("SELECT * FROM events", fetch=True)

    def delete_event(self, event_id):
        """Видаляє подію за її ID."""
        self.execute_query("DELETE FROM events WHERE id=?", (int(event_id),))


# Перевірка роботи модуля
if __name__ == "__main__":
    db = DatabaseManager()
    print("База даних успішно підключена та налаштована!")
