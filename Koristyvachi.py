import tkinter as tk
from tkinter import messagebox
import pyodbc


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
            messagebox.showerror("Помилка підключення", f"Не вдалося підключитись до бази даних: {str(e)}")
            raise SystemExit()

    def create_tables(self):
        """Створення таблиць, якщо вони не існують."""
        queries = [
            '''IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='users' AND xtype='U')
               CREATE TABLE users (
                   id INT IDENTITY(1,1) PRIMARY KEY,
                   name NVARCHAR(100),
                   email NVARCHAR(100),
                   phone NVARCHAR(20),
                   contact_method NVARCHAR(20)
               )''',
            '''IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='messages' AND xtype='U')
               CREATE TABLE messages (
                   id INT IDENTITY(1,1) PRIMARY KEY,
                   user_id INT,
                   message NVARCHAR(1000),
                   FOREIGN KEY (user_id) REFERENCES users(id)
               )'''
        ]
        for query in queries:
            self.cursor.execute(query)
        self.conn.commit()

    def execute_query(self, query, params=(), fetch=False):
        """Виконати SQL-запит."""
        with self.conn.cursor() as cursor:
            cursor.execute(query, params)
            if fetch:
                return cursor.fetchall()
            self.conn.commit()


class EventNotifierGUI:
    """Головний клас інтерфейсу програми."""

    def __init__(self, root, db_manager):
        self.root = root
        self.db = db_manager
        self.root.title("Система інформування користувачів")
        self.root.geometry("800x600")
        self.root.configure(bg="#e6f7e6")

        self.create_gui()
        self.load_users()

    def create_gui(self):
        """Створення графічного інтерфейсу."""
        tk.Label(self.root, text="Повідомлення для користувачів",
                 font=("Arial", 16), bg="#e6f7e6", fg="#333").pack(pady=10)

        self.users_listbox = tk.Listbox(self.root, height=6, width=45, font=("Arial", 12))
        self.users_listbox.pack(pady=10)

        tk.Label(self.root, text="Введіть повідомлення", bg="#e6f7e6", fg="#333").pack()
        self.message_entry = tk.Text(self.root, font=("Arial", 12), width=50, height=8)
        self.message_entry.pack(pady=10)

        tk.Button(self.root, text="Відправити повідомлення", font=("Arial", 12),
                  bg="#4CAF50", fg="#fff", command=self.send_message).pack(pady=20)

        buttons_frame = tk.Frame(self.root, bg="#e6f7e6")
        buttons_frame.pack(pady=20)

        tk.Button(buttons_frame, text="Додати користувача", font=("Arial", 12),
                  bg="#2196F3", fg="#fff", command=self.add_user).pack(side=tk.LEFT, padx=10)


        tk.Button(buttons_frame, text="Видалити користувача", font=("Arial", 12),
                  bg="#F44336", fg="#fff", command=self.delete_user).pack(side=tk.LEFT, padx=10)

    def load_users(self):
        """Завантаження списку користувачів."""
        self.users_listbox.delete(0, tk.END)
        users = self.db.execute_query("SELECT id, name, contact_method, email, phone FROM users", fetch=True)
        self.user_data = {}  # Зберігаємо ID користувачів у dict
        for user in users:
            user_id, name, method, email, phone = user
            contact_info = email if method == "email" else phone
            display_text = f"{name} ({method}: {contact_info})"
            self.users_listbox.insert(tk.END, display_text)
            self.user_data[display_text] = user_id

    def send_message(self):
        """Надсилання повідомлення вибраному користувачу."""
        selected = self.users_listbox.curselection()
        if not selected:
            messagebox.showwarning("Помилка", "Оберіть користувача зі списку.")
            return

        user_text = self.users_listbox.get(selected[0])
        user_id = self.user_data[user_text]

        message = self.message_entry.get("1.0", tk.END).strip()
        if not message:
            messagebox.showwarning("Помилка", "Введіть повідомлення.")
            return

        self.db.execute_query("INSERT INTO messages (user_id, message) VALUES (?, ?)", (user_id, message))
        messagebox.showinfo("Готово", "Повідомлення відправлено.")
        self.message_entry.delete("1.0", tk.END)

    def add_user(self):
        """Додавання користувача."""
        def save_user():
            name, email, phone = name_entry.get(), email_entry.get(), phone_entry.get()
            contact_method = contact_var.get()

            if not name or (contact_method == "email" and not email) or (contact_method == "phone" and not phone):
                messagebox.showwarning("Помилка", "Заповніть всі поля.")
                return

            self.db.execute_query("INSERT INTO users (name, email, phone, contact_method) VALUES (?, ?, ?, ?)",
                                  (name, email if contact_method == "email" else None,
                                   phone if contact_method == "phone" else None, contact_method))
            messagebox.showinfo("Готово", "Користувача додано.")
            new_user_window.destroy()
            self.load_users()

        new_user_window = tk.Toplevel(self.root)
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

        tk.Button(new_user_window, text="Зберегти", command=save_user).pack()

    def delete_user(self):
        """Видалення користувача."""
        selected = self.users_listbox.curselection()
        if not selected:
            messagebox.showwarning("Помилка", "Оберіть користувача зі списку.")
            return

        user_text = self.users_listbox.get(selected[0])
        user_id = self.user_data[user_text]

        self.db.execute_query("DELETE FROM users WHERE id=?", (user_id,))
        messagebox.showinfo("Готово", "Користувача видалено.")
        self.load_users()


if __name__ == "__main__":
    root = tk.Tk()
    db_manager = DatabaseManager()
    app = EventNotifierGUI(root, db_manager)
    root.mainloop()
