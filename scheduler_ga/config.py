from typing import Set

"""
Tham số đầu vào
"""

DATA_FILE = "data/data_input.json" 

# Ràng buộc mềm: Danh sách mã môn học được xem là "môn khó" (ưu tiên xếp buổi sáng).
MON_KHO_IDS: Set[str] = {"CS204", "AI202", "DS201"} 

# --- Trọng số cho Hàm Fitness ---
PHAT_CUNG = 1000          # Phạt cho vi phạm lỗi nặng (1 GV dạy 2 lớp cùng lúc, 1 phòng có 2 lớp cùng giờ, môn xếp ngoài thgian cho phép)
PHAT_MEM = 10             # Phạt cho vi phạm lỗi nhẹ (môn khó xếp buổi chiệu, lớp có quá nhiều tiết liên tục,...)
BASE_FITNESS_SCORE = 1000 # Điểm khởi đầu cho mỗi cá thể

# THAM SỐ THUẬT TOÁN GA
GA_POPULATION_SIZE = 60  # Số tkb của mỗi thế hệ
GA_GENERATIONS = 500      # Số thế hệ tối đa
GA_MUTATION_RATE = 0.15   # Xác suất đột biến
GA_ELITISM_COUNT = 5     # Số cá thể tốt nhất được giữ nguyên sang thế hệ sau

# Dùng cho PSO để so sánh với GA
PSO_SWARM_SIZE = 60
PSO_ITERATIONS = 500
PSO_W = 0.7
PSO_C1 = 2.0

PSO_C2 = 2.0
