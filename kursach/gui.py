import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from database import DatabaseManager
from user_manager import UserManager


class EventNotifierGUI:
    """Графічний інтерфейс для управління користувачами та подіями."""

    def __init__(self, root, db_manager):
        self.root = root
        self.root.title("Event Notifier")
        self.root.geometry("800x600")

        self.db_manager = db_manager
        self.user_manager = UserManager(db_manager)

        self.create_gui()
        self.load_users()
        self.load_events()

    def create_gui(self):
        """Створює графічний інтерфейс."""

        # Блок користувачів
        frame_users = ttk.LabelFrame(self.root, text="Користувачі")
        frame_users.pack(fill="both", expand=True, padx=10, pady=5)

        self.user_table = ttk.Treeview(frame_users, columns=("ID", "Ім'я", "Email", "Телефон", "Зв'язок"), show="headings")
        for col in ("ID", "Ім'я", "Email", "Телефон", "Зв'язок"):
            self.user_table.heading(col, text=col)

        self.user_table.pack(fill="both", expand=True)

        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(btn_frame, text="Додати користувача", command=self.open_add_user_window).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Редагувати", command=self.open_edit_user_window).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Видалити", command=self.delete_user).pack(side="left", padx=5)

        # Блок подій
        frame_events = ttk.LabelFrame(self.root, text="Події")
        frame_events.pack(fill="both", expand=True, padx=10, pady=5)

        self.event_table = ttk.Treeview(frame_events, columns=("ID", "Користувач", "Подія", "Дата"), show="headings")
        for col in ("ID", "Користувач", "Подія", "Дата"):
            self.event_table.heading(col, text=col)

        self.event_table.pack(fill="both", expand=True)

        event_btn_frame = ttk.Frame(self.root)
        event_btn_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(event_btn_frame, text="Додати подію", command=self.open_add_event_window).pack(side="left", padx=5)
        ttk.Button(event_btn_frame, text="Видалити подію", command=self.delete_event).pack(side="left", padx=5)

    def load_users(self):
        """Завантажує користувачів у таблицю."""
        self.user_table.delete(*self.user_table.get_children())
        users = self.user_manager.get_users()
        for user in users:
            self.user_table.insert("", "end", values=user)

    def load_events(self):
        """Завантажує події у таблицю."""
        self.event_table.delete(*self.event_table.get_children())
        events = self.user_manager.get_events()
        for event in events:
            self.event_table.insert("", "end", values=event)

    def open_add_user_window(self):
        """Вікно додавання користувача."""
        win = tk.Toplevel(self.root)
        win.title("Додати користувача")
        win.geometry("300x250")

        ttk.Label(win, text="Ім'я:").pack()
        name_entry = ttk.Entry(win)
        name_entry.pack()

        ttk.Label(win, text="Email:").pack()
        email_entry = ttk.Entry(win)
        email_entry.pack()

        ttk.Label(win, text="Телефон:").pack()
        phone_entry = ttk.Entry(win)
        phone_entry.pack()

        ttk.Label(win, text="Зв'язок (email/телефон):").pack()
        contact_entry = ttk.Entry(win)
        contact_entry.pack()

        def save_user():
            self.user_manager.add_user(name_entry.get(), email_entry.get(), phone_entry.get(), contact_entry.get())
            self.load_users()
            win.destroy()

        ttk.Button(win, text="Зберегти", command=save_user).pack(pady=10)

    def open_edit_user_window(self):
        """Вікно редагування користувача."""
        selected = self.user_table.selection()
        if not selected:
            messagebox.showerror("Помилка", "Виберіть користувача!")
            return

        user_id, name, email, phone, contact = self.user_table.item(selected, "values")

        win = tk.Toplevel(self.root)
        win.title("Редагувати користувача")
        win.geometry("300x250")

        ttk.Label(win, text="Ім'я:").pack()
        name_entry = ttk.Entry(win)
        name_entry.insert(0, name)
        name_entry.pack()

        ttk.Label(win, text="Email:").pack()
        email_entry = ttk.Entry(win)
        email_entry.insert(0, email)
        email_entry.pack()

        ttk.Label(win, text="Телефон:").pack()
        phone_entry = ttk.Entry(win)
        phone_entry.insert(0, phone)
        phone_entry.pack()

        ttk.Label(win, text="Зв'язок:").pack()
        contact_entry = ttk.Entry(win)
        contact_entry.insert(0, contact)
        contact_entry.pack()

        def update_user():
            self.user_manager.update_user(user_id, name_entry.get(), email_entry.get(), phone_entry.get(), contact_entry.get())
            self.load_users()
            win.destroy()

        ttk.Button(win, text="Зберегти", command=update_user).pack(pady=10)

    def delete_user(self):
        """Видаляє вибраного користувача."""
        selected = self.user_table.selection()
        if not selected:
            messagebox.showerror("Помилка", "Виберіть користувача!")
            return

        user_id = self.user_table.item(selected, "values")[0]
        self.user_manager.delete_user(user_id)
        self.load_users()

    def open_add_event_window(self):
        """Вікно додавання події."""
        win = tk.Toplevel(self.root)
        win.title("Додати подію")
        win.geometry("300x200")

        users = self.user_manager.get_users()
        user_choices = {f"{user[0]} - {user[1]}": user[0] for user in users}

        ttk.Label(win, text="Користувач:").pack()
        user_var = tk.StringVar()
        user_dropdown = ttk.Combobox(win, textvariable=user_var, values=list(user_choices.keys()))
        user_dropdown.pack()

        ttk.Label(win, text="Подія:").pack()
        event_entry = ttk.Entry(win)
        event_entry.pack()

        ttk.Label(win, text="Дата:").pack()
        date_entry = DateEntry(win)
        date_entry.pack()

        def save_event():
            user_id = user_choices.get(user_var.get())
            if user_id:
                self.user_manager.add_event(user_id, event_entry.get(), date_entry.get_date())
                self.load_events()
                win.destroy()

        ttk.Button(win, text="Зберегти", command=save_event).pack(pady=10)

    def delete_event(self):
        """Видаляє подію."""
        selected = self.event_table.selection()
        if not selected:
            messagebox.showerror("Помилка", "Виберіть подію!")
            return

        event_id = self.event_table.item(selected, "values")[0]
        self.user_manager.delete_event(event_id)
        self.load_events()


if __name__ == "__main__":
    root = tk.Tk()
    db = DatabaseManager()
    app = EventNotifierGUI(root, db)
    root.mainloop()
