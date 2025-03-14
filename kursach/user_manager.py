import tkinter as tk
from tkinter import messagebox


class UserManager:
    """Клас для керування користувачами."""

    def __init__(self, db_manager, update_users_callback):
        self.db = db_manager
        self.update_users_callback = update_users_callback

    def open_add_user_window(self):
        """Відкриває вікно для додавання користувача."""
        new_user_window = tk.Toplevel()
        new_user_window.title("Додати користувача")
        new_user_window.geometry("400x300")

        tk.Label(new_user_window, text="Ім'я").pack()
        name_entry = tk.Entry(new_user_window)
        name_entry.pack()

        tk.Label(new_user_window, text="Електронна пошта").pack()
        email_entry = tk.Entry(new_user_window)
        email_entry.pack()

        tk.Label(new_user_window, text="Номер телефону").pack()
        phone_entry = tk.Entry(new_user_window)
        phone_entry.pack()

        contact_var = tk.StringVar(value="email")
        tk.Radiobutton(new_user_window, text="Email", variable=contact_var, value="email").pack()
        tk.Radiobutton(new_user_window, text="Телефон", variable=contact_var, value="phone").pack()

        tk.Button(new_user_window, text="Зберегти", command=lambda: self.save_user(
            name_entry.get(), email_entry.get(), phone_entry.get(), contact_var.get(), new_user_window
        )).pack()

    def save_user(self, name, email, phone, contact_method, window):
        """Зберігає нового користувача в базу."""
        if not name or (contact_method == "email" and not email) or (contact_method == "phone" and not phone):
            messagebox.showwarning("Помилка", "Заповніть всі поля.")
            return

        self.db.execute_query("INSERT INTO users (name, email, phone, contact_method) VALUES (?, ?, ?, ?)",
                              (name, email if contact_method == "email" else None,
                               phone if contact_method == "phone" else None, contact_method))
        messagebox.showinfo("Готово", "Користувача додано.")
        window.destroy()
        self.update_users_callback()
