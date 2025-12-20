import tkinter as tk
from ui.gui import SchedulerGUI

def main():
    """
    Khởi tạo và hiển thị giao diện người dùng.
    """
    root = tk.Tk()
    root.title("Ứng dụng Xếp Lịch Học")
    root.geometry("1000x750")

    app = SchedulerGUI(root)

    root.mainloop()

if __name__ == "__main__":
    main()