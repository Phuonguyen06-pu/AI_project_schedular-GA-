import tkinter as tk
from tkinter import ttk, messagebox
from threading import Thread
import time
from typing import Optional, List, Tuple

# Import các module nội bộ
from config import * 
from data.data_loader import GlobalDataManager 
from algorithms import ga, pso 
from algorithms.models import Schedule 
from algorithms.utils import generate_base_assignments 
from core.fitness import calculate_fitness 

class SchedulerGUI:
    """Giao diện xếp lịch học """

    def __init__(self, master):
        self.master = master
        self.data_manager: Optional[GlobalDataManager] = None
        self.base_assignments: List[Tuple] = []
        self.last_best_schedule: Optional[Schedule] = None 
        
        self.ga_widgets = []
        self.pso_widgets = []
        
        self._setup_ui()

    def _setup_ui(self):
        """Giao diện người dùng chính."""
        style = ttk.Style()
        style.theme_use('vista') 
        style.configure("Matrix.Treeview", rowheight=65, font=("Segoe UI", 9))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        
        # nút tải dữ liệu và bắt đầu
        top_frame = ttk.Frame(self.master)
        top_frame.pack(padx=10, pady=10, fill="x")
        
        self.load_btn = ttk.Button(top_frame, text="1. Tải Dữ liệu", command=self._load_data)
        self.load_btn.pack(side=tk.LEFT, padx=5)
        
        self.run_btn = ttk.Button(top_frame, text="2. BẮT ĐẦU XẾP LỊCH", command=self._start_solver_thread, state=tk.DISABLED)
        self.run_btn.pack(side=tk.LEFT, padx=10)

        # khung cấu hình thuật toán và báo cáo kết quả
        upper_main_frame = ttk.Frame(self.master)
        upper_main_frame.pack(padx=10, pady=5, fill="x")
        
        config_frame = ttk.LabelFrame(upper_main_frame, text="Cấu hình Thuật toán")
        config_frame.pack(side=tk.LEFT, fill="both", expand=True, padx=(0, 10))

        # Chọn thuật toán
        self.algorithm_var = tk.StringVar(value="GA")
        ttk.Radiobutton(config_frame, text="GA", variable=self.algorithm_var, value="GA", command=self._update_widget_states).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        ttk.Radiobutton(config_frame, text="PSO", variable=self.algorithm_var, value="PSO", command=self._update_widget_states).grid(row=0, column=1, padx=10, pady=5, sticky="w")
        
        # Các thông số thuật toán
        self.ga_pop_entry = self._create_entry(config_frame, "Kích thước quần thể (GA):", GA_POPULATION_SIZE, 1, 0)
        self.ga_gen_entry = self._create_entry(config_frame, "Số thế hệ (GA):", GA_GENERATIONS, 1, 2)
        self.pso_iter_entry = self._create_entry(config_frame, "Vòng lặp PSO:", PSO_ITERATIONS, 1, 4)

        self.ga_mut_entry = self._create_entry(config_frame, "Tỷ lệ đột biến (GA):", GA_MUTATION_RATE, 2, 0)
        self.ga_elit_entry = self._create_entry(config_frame, "Cá thể ưu tú (GA):", GA_ELITISM_COUNT, 2, 2)
        self.pso_swarm_entry = self._create_entry(config_frame, "Kích thước bầy (PSO):", PSO_SWARM_SIZE, 2, 4)

        self.ga_widgets = [self.ga_pop_entry, self.ga_gen_entry, self.ga_mut_entry, self.ga_elit_entry]
        self.pso_widgets = [self.pso_iter_entry, self.pso_swarm_entry]

        # Báo cáo kết quả
        result_pane = ttk.LabelFrame(upper_main_frame, text="📊 Báo cáo Kết quả")
        result_pane.pack(side=tk.RIGHT, fill="both", ipadx=10)

        self.res_fit_lbl = ttk.Label(result_pane, text="Fitness: ---", font=("Segoe UI", 10, "bold"))
        self.res_fit_lbl.grid(row=0, column=0, padx=15, pady=5, sticky="w")
        self.res_hard_lbl = ttk.Label(result_pane, text="Lỗi Cứng: ---", foreground="red", font=("Segoe UI", 9, "bold"))
        self.res_hard_lbl.grid(row=1, column=0, padx=15, pady=5, sticky="w")
        self.res_soft_lbl = ttk.Label(result_pane, text="Lỗi Mềm: ---", foreground="#CC7A00", font=("Segoe UI", 9, "bold"))
        self.res_soft_lbl.grid(row=0, column=1, padx=15, pady=5, sticky="w")
        self.res_time_lbl = ttk.Label(result_pane, text="Thời gian: ---", font=("Segoe UI", 9))
        self.res_time_lbl.grid(row=1, column=1, padx=15, pady=5, sticky="w")

        self.res_stats_lbl = ttk.Label(result_pane, text="Thành công: Lớp --/--, GV --/--", font=("Segoe UI", 9, "italic"))
        self.res_stats_lbl.grid(row=2, column=0, columnspan=2, padx=15, pady=5, sticky="w")

        # Thanh trạng thái
        self.status_label = ttk.Label(self.master, text="Trạng thái: Sẵn sàng", font=('Arial', 9, 'italic'))
        self.status_label.pack(padx=10, fill="x", pady=5)

        # Tab điều hướng kết quả
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(padx=10, pady=5, fill="both", expand=True)

        # TAB 1: LỊCH TỔNG QUÁT (DẠNG DANH SÁCH GỐC)
        self.tab_general = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_general, text="📅 Lịch Tổng Quát")
        self._setup_general_tab()

        # TAB 2: TRUY VẤN CHI TIẾT (DẠNG MA TRẬN)
        self.tab_query = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_query, text="🔍 Lịch Chi Tiết (GV/Lớp)")
        self._setup_query_tab()

        self._update_widget_states()

    def _create_entry(self, parent, label, default, row, col):
        '''Tạo một cặp nhãn và ô nhập liệu trong lưới.'''
        ttk.Label(parent, text=label).grid(row=row, column=col, padx=5, sticky="e")
        entry = ttk.Entry(parent, width=10)
        entry.insert(0, str(default))
        entry.grid(row=row, column=col+1, sticky="w", pady=5)
        return entry

    def _update_widget_states(self):
        for w in self.ga_widgets + self.pso_widgets:
            w.configure(state='readonly')

    def _setup_general_tab(self):
        """Bảng danh sách toàn bộ lịch học giúp bao quát nhanh"""
        cols = ("mon", "lop", "gv", "phong", "buoi")
        self.result_table = ttk.Treeview(self.tab_general, columns=cols, show='headings')
        self.result_table.heading("mon", text="MÔN HỌC")
        self.result_table.heading("lop", text="LỚP")
        self.result_table.heading("gv", text="GIẢNG VIÊN")
        self.result_table.heading("phong", text="PHÒNG")
        self.result_table.heading("buoi", text="BUỔI HỌC")
        
        self.result_table.column("mon", width=280)
        self.result_table.column("lop", width=80, anchor="center")
        self.result_table.column("gv", width=180)
        self.result_table.column("phong", width=80, anchor="center")
        self.result_table.column("buoi", width=130, anchor="center")
        
        self.result_table.tag_configure('oddrow', background='#f2f2f2')
        self.result_table.pack(side=tk.LEFT, fill="both", expand=True)
        
        self.result_table.pack(side=tk.LEFT, fill="both", expand=True)
        scrollbar = ttk.Scrollbar(self.tab_general, orient=tk.VERTICAL, command=self.result_table.yview)
        self.result_table.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill="y")
   
   
    def _setup_query_tab(self):
        """Giao diện ma trận với độ rộng cột tối ưu cho tên môn học dài"""
        filter_frame = ttk.Frame(self.tab_query)
        filter_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(filter_frame, text="Truy vấn theo:").pack(side=tk.LEFT)
        self.query_type_var = tk.StringVar(value="Giảng viên")
        self.type_combo = ttk.Combobox(filter_frame, textvariable=self.query_type_var, values=["Giảng viên", "Lớp"], state="readonly", width=15)
        self.type_combo.pack(side=tk.LEFT, padx=5)
        self.type_combo.bind("<<ComboboxSelected>>", self._update_object_list)

        ttk.Label(filter_frame, text="Chi tiết:").pack(side=tk.LEFT, padx=(10, 0))
        self.object_var = tk.StringVar()
        self.object_combo = ttk.Combobox(filter_frame, textvariable=self.object_var, state="readonly", width=40)
        self.object_combo.pack(side=tk.LEFT, padx=5)
        self.object_combo.bind("<<ComboboxSelected>>", self._update_matrix_view)

        # Bảng ma trận thời khóa biểu
        matrix_cols = ("session", "t2", "t3", "t4", "t5", "t6", "t7")
        self.matrix_table = ttk.Treeview(self.tab_query, columns=matrix_cols, show='headings', height=3, style="Matrix.Treeview")
        
        days = ["BUỔI", "Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7"]
        for col, name in zip(matrix_cols, days):
            self.matrix_table.heading(col, text=name.upper())
            width = 180 if col != "session" else 85
            self.matrix_table.column(col, width=width, anchor="center")
        
        self.matrix_table.pack(padx=10, pady=10, fill="x")
        ttk.Label(self.tab_query, text="* Lưu ý: Có thể điều chỉnh độ rộng cột để xem đầy đủ thông tin", font=("Arial", 8, "italic")).pack(padx=10, anchor="w")

    def _update_object_list(self, event=None):
        if not self.data_manager: return
        if self.query_type_var.get() == "Giảng viên":
            vals = sorted([gv.name for gv in self.data_manager.lecturers])
        else:
            vals = sorted([lp.code for lp in self.data_manager.class_groups])
        self.object_combo['values'] = vals
        self.object_var.set("")

    def _update_matrix_view(self, event=None):
        target = self.object_var.get()
        q_type = self.query_type_var.get()
        for item in self.matrix_table.get_children(): self.matrix_table.delete(item)
        if not self.last_best_schedule or not target: return

        matrix = {"SANG": ["SÁNG", "", "", "", "", "", ""], "CHIEU": ["CHIỀU", "", "", "", "", "", ""]}
        for a in self.last_best_schedule.assignments:
            match = (q_type == "Giảng viên" and a.lecturer.name == target) or \
                    (q_type == "Lớp" and a.class_group.code == target)
            if match and a.time_slot:
                col_idx = a.time_slot.day - 1 
                sub_name = a.subject.name
                matrix[a.time_slot.session][col_idx] = f"{sub_name}\n({a.room.code})\n{'Lớp: '+a.class_group.code if q_type=='Giảng viên' else 'GV: '+a.lecturer.name}"

        self.matrix_table.insert("", tk.END, values=matrix["SANG"])
        self.matrix_table.insert("", tk.END, values=matrix["CHIEU"])

    def _load_data(self):
        '''tải dữ liệu từ file'''
        try:
            self.data_manager = GlobalDataManager.load_data(DATA_FILE)
            self.base_assignments = generate_base_assignments(self.data_manager)
            self.status_label.config(text="✅ Nạp dữ liệu thành công!", foreground="blue")
            self.run_btn.config(state=tk.NORMAL)
            self._update_object_list()
        except Exception as e:
            messagebox.showerror("Lỗi dữ liệu", str(e))

    def _start_solver_thread(self):
        '''chạy thuật toán trong luồng riêng để không làm đơ giao diện'''
        self.run_btn.config(state=tk.DISABLED); self.load_btn.config(state=tk.DISABLED)
        for item in self.result_table.get_children(): self.result_table.delete(item)
        
        algo = self.algorithm_var.get()
        config = {
            'pop_size': int(self.ga_pop_entry.get()), 
            'generations': int(self.ga_gen_entry.get()),
            'mutation_rate': float(self.ga_mut_entry.get()),
            'elitism_count': int(self.ga_elit_entry.get()),
            'iterations': int(self.pso_iter_entry.get()),
            'swarm_size': int(self.pso_swarm_entry.get())
        }
        self.status_label.config(text=f"⌛ Đang thực hiện thuật toán {algo}...", foreground="black")
        Thread(target=self._run_solver_logic, args=(algo, config)).start()

    def _run_solver_logic(self, algorithm, config):
        '''hàm chạy thuật toán và cập nhật giao diện'''
        start_time = time.time()
        def callback(curr, tot, best): self.master.after(0, self._update_progress, curr, tot, best)
        try:
            if algorithm == "GA":
                best = ga.run_ga(self.data_manager, self.base_assignments, config, callback)
            else:
                best = pso.run_pso(self.data_manager, self.base_assignments, config, callback)
            
            self.last_best_schedule = best
            self.master.after(0, self._display_final_result, best, time.time() - start_time)
        except Exception as e:
            self.master.after(0, lambda: messagebox.showerror("Lỗi", str(e)))
            self.master.after(0, self._reset_buttons)

    def _update_progress(self, curr, tot, best):
        '''cập nhật tiến độ thuật toán trên giao diện'''
        self.status_label.config(text=f"🔄 Tiến độ: {curr}/{tot} thế hệ")
        self.res_fit_lbl.config(text=f"Fitness: {best.fitness:.2f}")
        self.res_hard_lbl.config(text=f"Lỗi Cứng: {best.hard_violations}")

    def _reset_buttons(self):
        self.run_btn.config(state=tk.NORMAL); self.load_btn.config(state=tk.NORMAL)

    def _display_final_result(self, best, exec_time):
        '''hiển thị kết quả cuối cùng lên giao diện'''
        self.res_fit_lbl.config(text=f"Fitness: {best.fitness:,.2f}")
        self.res_hard_lbl.config(text=f"Lỗi Cứng: {best.hard_violations}")
        self.res_soft_lbl.config(text=f"Lỗi Mềm: {best.soft_violations}")
        self.res_time_lbl.config(text=f"Thời gian: {exec_time:.2f} s")
        
        # tính tổng số lớp và gv
        total_cls = len(self.data_manager.class_groups)
        total_gv = len(self.data_manager.lecturers)
    
        # tính số lớp và gv xếp lịch thành công
        success_cls = max(0, total_cls - min(best.hard_violations, total_cls)) if best.hard_violations > 0 else total_cls
        success_gv = max(0, total_gv - min(best.hard_violations, total_gv)) if best.hard_violations > 0 else total_gv
    
        self.res_stats_lbl.config(text=f"Thành công: Lớp {success_cls}/{total_cls}, GV {success_gv}/{total_gv}")
    
        ds = sorted(best.assignments, key=lambda x: (x.time_slot.day if x.time_slot else 9, 0 if x.time_slot and x.time_slot.session == "SANG" else 1))
        for a in ds:
            tg = f"Thứ {a.time_slot.day} ({'Sáng' if a.time_slot.session == 'SANG' else 'Chiều'})" if a.time_slot else "N/A"
            self.result_table.insert("", tk.END, values=(a.subject.name, a.class_group.code, a.lecturer.name, a.room.code, tg))
        
        self.status_label.config(text=f"✅ Hoàn thành sau {exec_time:.2f} giây.", foreground="green")
        self._reset_buttons(); self._update_matrix_view()