import tkinter as tk
from tkinter import messagebox
from database import DatabaseManager
from user_manager import UserManager


class EventNotifierGUI:
    """Головний клас інтерфейсу програми."""

    def __init__(self, root, db_manager):
        self.root = root
        self.db = db_manager
        self.root.title("Система інформування користувачів")
        self.root.geometry("800x600")
        self.root.configure(bg="#e6f7e6")

        self.user_manager = UserManager(self.db, self.load_users)  # Використання UserManager

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
                  bg="#2196F3", fg="#fff", command=self.user_manager.open_add_user_window).pack(side=tk.LEFT, padx=10)

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
