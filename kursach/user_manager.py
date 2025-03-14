import pyodbc
from database import DatabaseManager
from tkinter import messagebox


class UserManager:
    """Клас для управління користувачами та подіями."""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    # === Управління користувачами ===
    def add_user(self, name, email, phone, contact_method):
        """Додає нового користувача в базу даних."""
        if not name or not contact_method:
            messagebox.showerror("Помилка", "Ім'я та спосіб зв'язку обов'язкові!")
            return

        self.db.execute_query(
            "INSERT INTO users (name, email, phone, contact_method) VALUES (?, ?, ?, ?)",
            (name, email, phone, contact_method),
        )
        messagebox.showinfo("Успіх", "Користувач доданий!")

    def get_users(self):
        """Повертає список усіх користувачів."""
        users = self.db.execute_query("SELECT * FROM users", fetch=True)
        return users if users else []  # Уникаємо None

    def update_user(self, user_id, name, email, phone, contact_method):
        """Оновлює інформацію про користувача."""
        self.db.execute_query(
            "UPDATE users SET name=?, email=?, phone=?, contact_method=? WHERE id=?",
            (name, email, phone, contact_method, user_id),
        )
        messagebox.showinfo("Успіх", "Дані користувача оновлено!")

    def delete_user(self, user_id):
        """Видаляє користувача та пов'язані з ним події."""
        self.db.execute_query("DELETE FROM events WHERE user_id=?", (user_id,))
        self.db.execute_query("DELETE FROM users WHERE id=?", (user_id,))
        messagebox.showinfo("Успіх", "Користувач видалений!")

    # === Управління подіями ===
    def add_event(self, user_id, event_name, event_date):
        """Додає подію для користувача."""
        if not event_name or not event_date:
            messagebox.showerror("Помилка", "Назва події та дата обов'язкові!")
            return

        if not isinstance(user_id, int):
            messagebox.showerror("Помилка", "Невірний ідентифікатор користувача!")
            return

        existing_user = self.db.execute_query("SELECT id FROM users WHERE id=?", (user_id,), fetch=True)
        if not existing_user:
            messagebox.showerror("Помилка", "Користувач не знайдений!")
            return

        self.db.execute_query(
            "INSERT INTO events (user_id, event_name, event_date) VALUES (?, ?, ?)",
            (user_id, event_name, event_date),
        )
        messagebox.showinfo("Успіх", "Подія додана!")

    def get_events(self):
        """Повертає всі події."""
        events = self.db.execute_query("SELECT * FROM events", fetch=True)
        return events if events else []  # Уникаємо None

    def delete_event(self, event_id):
        """Видаляє подію."""
        self.db.execute_query("DELETE FROM events WHERE id=?", (event_id,))
        messagebox.showinfo("Успіх", "Подія видалена!")


# === Перевірка модуля ===
if __name__ == "__main__":
    db = DatabaseManager()
    manager = UserManager(db)

    # Додавання тестового користувача
    manager.add_user("Іван Петров", "ivan@example.com", "1234567890", "email")

    # Отримання користувачів
    users = manager.get_users()
    if users:
        manager.add_event(users[0][0], "Зустріч", "2025-03-20 10:00:00")

    print("Користувачі:", manager.get_users())
    print("Події:", manager.get_events())
