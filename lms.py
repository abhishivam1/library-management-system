import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os

BOOKS_FILE = "books.csv"
USERS_FILE = "users.csv"
BORROWED_FILE = "borrowed.csv"

def read_csv(file, fields):
    if not os.path.exists(file):
        f = open(file, "a", newline="")
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        f.close()
    f = open(file, newline="")
    data = list(csv.DictReader(f))
    f.close()
    return data

def append_csv(file, row, fields):
    file_exists = os.path.exists(file)
    f = open(file, "a", newline="")
    writer = csv.DictWriter(f, fieldnames=fields)
    if not file_exists or os.stat(file).st_size == 0:
        writer.writeheader()
    writer.writerow(row)
    f.close()

def write_all_csv(file, data, fields):
    f = open(file, "w", newline="")
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(data)
    f.close()

class LibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Library Management System")
        self.root.geometry("900x600")

        self.left_panel = tk.Frame(root, width=250, bg="#000000")
        self.left_panel.pack(side="left", fill="y")

        tk.Button(self.left_panel, text="Books", width=20, height=2, command=self.show_books_tab, bg="#ffffff", fg="black", font=("Segoe UI", 18, "bold")).pack(pady=20)
        tk.Button(self.left_panel, text="Books Borrowed", width=20, height=2, command=self.show_borrowed_tab, bg="#ffffff", fg="black", font=("Segoe UI", 18, "bold")).pack(pady=20)
        tk.Button(self.left_panel, text="Users", width=20, height=2, command=self.show_users_tab, bg="#ffffff", fg="black", font=("Segoe UI", 18, "bold")).pack(pady=20)

        self.right_panel = tk.Frame(root, bg="#ffffff")
        self.right_panel.pack(side="right", fill="both", expand=True)

        self.show_books_tab()

    def clear_right_panel(self):
        for widget in self.right_panel.winfo_children():
            widget.destroy()

    def show_books_tab(self):
        self.clear_right_panel()
        title_frame = tk.Frame(self.right_panel, bg="#000000")
        title_frame.pack(fill="x", pady=10)
        tk.Label(title_frame, text="Books", font=("Segoe UI", 30, "bold"), bg="#000000", fg="white").pack(pady=10)

        self.books = read_csv(BOOKS_FILE, ["title", "author", "available"])

        self.book_tree = ttk.Treeview(self.right_panel, columns=("Title", "Author", "Available"), show="headings", height=10)
        self.book_tree.heading("Title", text="Title")
        self.book_tree.heading("Author", text="Author")
        self.book_tree.heading("Available", text="Available")
        self.book_tree.pack(fill="both", expand=True, padx=10)

        self.refresh_books()

        form = tk.Frame(self.right_panel, bg="#ffffff")
        form.pack(pady=20)
        tk.Button(form, text="Add Book", command=self.open_add_book_popup, height=2, width=18, bg="#28a745", fg="white", font=("Segoe UI", 16, "bold")).pack(side="left", padx=5)
        tk.Button(form, text="Remove Selected", command=self.remove_selected_book, height=2, width=18, bg="#dc3545", fg="white", font=("Segoe UI", 16, "bold")).pack(side="left", padx=5)
        tk.Button(form, text="Borrow Selected Book", command=self.borrow_selected_book, height=2, width=18, bg="#007bff", fg="white", font=("Segoe UI", 16, "bold")).pack(side="left", padx=5)

    def refresh_books(self):
        self.books = read_csv(BOOKS_FILE, ["title", "author", "available"])
        for i in self.book_tree.get_children():
            self.book_tree.delete(i)
        for book in self.books:
            self.book_tree.insert('', 'end', values=(book["title"], book["author"], book["available"]))

    def open_add_book_popup(self):
        popup = tk.Toplevel(self.root)
        popup.title("Add New Book")
        popup.geometry("300x300")
        popup.resizable(False, False)

        tk.Label(popup, text="Title:", font=("Segoe UI", 18), bg="#ffffff").pack(pady=10)
        title_var = tk.StringVar()
        tk.Entry(popup, textvariable=title_var, font=("Segoe UI", 18), width=25).pack()

        tk.Label(popup, text="Author:", font=("Segoe UI", 18), bg="#ffffff").pack(pady=10)
        author_var = tk.StringVar()
        tk.Entry(popup, textvariable=author_var, font=("Segoe UI", 18), width=25).pack()

        borrowable_var = tk.BooleanVar(value=True)
        tk.Checkbutton(popup, text="Allow Borrow", variable=borrowable_var, font=("Segoe UI", 18), bg="#ffffff").pack(pady=10)

        def submit():
            title = title_var.get().strip()
            author = author_var.get().strip()
            if not title or not author:
                messagebox.showwarning("Missing info", "Enter both title and author.")
                return
            new_book = {
                "title": title,
                "author": author,
                "available": "True" if borrowable_var.get() else "False"
            }
            append_csv(BOOKS_FILE, new_book, ["title", "author", "available"])
            self.refresh_books()
            popup.destroy()

        tk.Button(popup, text="Add Book", command=submit, height=2, width=18, bg="#28a745", fg="white", font=("Segoe UI", 16, "bold")).pack(pady=10)

    def remove_selected_book(self):
        selected = self.book_tree.selection()
        if not selected:
            return
        values = self.book_tree.item(selected[0])["values"]
        self.books = [b for b in self.books if not (b["title"] == values[0] and b["author"] == values[1])]
        write_all_csv(BOOKS_FILE, self.books, ["title", "author", "available"])
        self.refresh_books()

    def borrow_selected_book(self):
        selected = self.book_tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Please select a book.")
            return

        book_values = self.book_tree.item(selected[0])["values"]
        if book_values[2] != "True":
            messagebox.showerror("Unavailable", "Book is not available for borrowing.")
            return

        def confirm_borrow():
            name = name_var.get().strip()
            user_id = user_id_var.get().strip()
            if not name or not user_id:
                messagebox.showwarning("Missing Info", "Please enter both name and ID.")
                return

            users = read_csv(USERS_FILE, ["name", "id", "borrowed"])
            existing_user = next((u for u in users if u["name"] == name and u["id"] == user_id), None)

            if not existing_user:
                messagebox.showinfo("User Added", f"Student '{name}' with ID '{user_id}' added automatically.")
                new_user = {"name": name, "id": user_id, "borrowed": ""}
                append_csv(USERS_FILE, new_user, ["name", "id", "borrowed"])
                users.append(new_user)

            for u in users:
                if u["id"] == user_id:
                    u["borrowed"] = (u["borrowed"] + ", " if u["borrowed"] else "") + book_values[0]
            write_all_csv(USERS_FILE, users, ["name", "id", "borrowed"])

            books = read_csv(BOOKS_FILE, ["title", "author", "available"])
            for b in books:
                if b["title"] == book_values[0] and b["author"] == book_values[1]:
                    b["available"] = "False"
            write_all_csv(BOOKS_FILE, books, ["title", "author", "available"])
            self.refresh_books()

            append_csv(BORROWED_FILE, {
                "book": book_values[0],
                "user": name,
                "user_id": user_id
            }, ["book", "user", "user_id"])

            popup.destroy()
            messagebox.showinfo("Success", f"Book '{book_values[0]}' borrowed to {name} (ID: {user_id})")

        name_var = tk.StringVar()
        user_id_var = tk.StringVar()

        popup = tk.Toplevel(self.root)
        popup.title("Borrow Book")
        popup.geometry("350x200")
        popup.resizable(False, False)
        tk.Label(popup, text="Enter Student Name:", font=("Segoe UI", 18), bg="#f4f4f4").pack(pady=5)
        tk.Entry(popup, textvariable=name_var, font=("Segoe UI", 18), width=25).pack(pady=5)

        tk.Label(popup, text="Enter Student ID:", font=("Segoe UI", 18), bg="#f4f4f4").pack(pady=5)
        tk.Entry(popup, textvariable=user_id_var, font=("Segoe UI", 18), width=25).pack(pady=5)

        tk.Button(popup, text="Confirm Borrow", command=confirm_borrow, height=2, width=18, bg="#28a745", fg="white", font=("Segoe UI", 16, "bold")).pack(pady=10)

    def return_selected_borrowed_book(self):
        selected = self.book_tree.selection()

        if not selected:
            messagebox.showwarning("No selection", "Please select a borrowed book.")
            return

        values = self.book_tree.item(selected[0])["values"]
        book_to_return = values[0]
        user_to_return = values[1]

        books = read_csv(BOOKS_FILE, ["title", "author", "available"])
        for b in books:
            if b["title"] == book_to_return:
                b["available"] = "True"
        write_all_csv(BOOKS_FILE, books, ["title", "author", "available"])

        borrowed = read_csv(BORROWED_FILE, ["book", "user", "user_id"])
        borrowed = [b for b in borrowed if not (b["book"] == book_to_return and b["user"] == user_to_return)]
        write_all_csv(BORROWED_FILE, borrowed, ["book", "user", "user_id"])

        self.show_borrowed_tab()

        messagebox.showinfo("Book Returned", f"Book '{book_to_return}' has been successfully returned.")

    def show_borrowed_tab(self):
        self.clear_right_panel()
        title_frame = tk.Frame(self.right_panel, bg="#000000") 
        title_frame.pack(fill="x", pady=10)
        tk.Label(title_frame, text="Books Borrowed", font=("Segoe UI", 30, "bold"), bg="#000000", fg="white").pack(pady=10)

        borrowed = read_csv(BORROWED_FILE, ["book", "user", "user_id"])

        tree = ttk.Treeview(self.right_panel, columns=("Book", "User", "User ID"), show="headings", height=10)
        tree.heading("Book", text="Book")
        tree.heading("User", text="User")
        tree.heading("User ID", text="User ID")
        tree.pack(fill="both", expand=True, padx=10)

        for row in borrowed:
            tree.insert('', 'end', values=(row["book"], row["user"], row["user_id"]))

        form = tk.Frame(self.right_panel, bg="#ffffff")
        form.pack(pady=20)

        self.return_button = tk.Button(form, text="Return Selected Book", command=self.return_selected_borrowed_book, height=2, width=18, bg="#dc3545", fg="white", font=("Segoe UI", 16, "bold"))
        self.return_button.pack()

    def show_users_tab(self):
        self.clear_right_panel()
        title_frame = tk.Frame(self.right_panel, bg="#000000") 
        title_frame.pack(fill="x", pady=10)
        tk.Label(title_frame, text="Users", font=("Segoe UI", 30, "bold"), bg="#000000", fg="white").pack(pady=10)

        self.users = read_csv(USERS_FILE, ["name", "id", "borrowed"])

        self.user_tree = ttk.Treeview(self.right_panel, columns=("Name", "ID", "Borrowed"), show="headings", height=10)
        self.user_tree.heading("Name", text="Name")
        self.user_tree.heading("ID", text="ID")
        self.user_tree.heading("Borrowed", text="Borrowed Books")
        self.user_tree.pack(fill="both", expand=True, padx=10)

        self.refresh_users()

        form = tk.Frame(self.right_panel, bg="#ffffff")
        form.pack(pady=20)

        self.user_name = tk.StringVar()
        self.user_id = tk.StringVar()

        self.add_user_button = tk.Button(form, text="Add User", command=self.show_user_input_fields, height=2, width=18, bg="#28a745", fg="white", font=("Segoe UI", 16, "bold"))
        self.add_user_button.pack(side="left", padx=5)

        tk.Button(form, text="Remove Selected", command=self.remove_selected_user, height=2, width=18, bg="#dc3545", fg="white", font=("Segoe UI", 16, "bold")).pack(side="left", padx=5)

    def show_user_input_fields(self):
        form = tk.Frame(self.right_panel, bg="#ffffff")
        form.pack(pady=20)
        
        tk.Label(form, text="Name:", font=("Segoe UI", 18), bg="#ffffff").pack(side="left", padx=5)
        tk.Entry(form, textvariable=self.user_name, font=("Segoe UI", 18), width=25).pack(side="left", padx=5)
        
        tk.Label(form, text="ID:", font=("Segoe UI", 18), bg="#ffffff").pack(side="left", padx=5)
        tk.Entry(form, textvariable=self.user_id, font=("Segoe UI", 18), width=25).pack(side="left", padx=5)

        tk.Button(form, text="Submit", command=self.add_user, height=2, width=18, bg="#28a745", fg="white", font=("Segoe UI", 16, "bold")).pack(side="left", padx=5)

    def add_user(self):
        name = self.user_name.get().strip()
        uid = self.user_id.get().strip()
        if name and uid:
            append_csv(USERS_FILE, {"name": name, "id": uid, "borrowed": ""}, ["name", "id", "borrowed"])
            self.refresh_users()
            self.user_name.set("")
            self.user_id.set("")
        else:
            messagebox.showwarning("Missing info", "Enter both name and ID.")

    def remove_selected_user(self):
        selected = self.user_tree.selection()
        
        if not selected:
            messagebox.showwarning("No selection", "Please select a user.")
            return

        values = self.user_tree.item(selected[0])["values"]
        name_to_remove = values[0]
        id_to_remove = values[1]
        
        self.users = [user for user in self.users if not (user["name"] == name_to_remove and user["id"] == id_to_remove)]
        
        write_all_csv(USERS_FILE, self.users, ["name", "id", "borrowed"])
        self.refresh_users()

    def refresh_users(self):
        self.users = read_csv(USERS_FILE, ["name", "id", "borrowed"])
        for i in self.user_tree.get_children():
            self.user_tree.delete(i)
        for user in self.users:
            self.user_tree.insert('', 'end', values=(user["name"], user["id"], user["borrowed"]))

if __name__ == "__main__":
    root = tk.Tk()
    app = LibraryApp(root)
    root.mainloop()
