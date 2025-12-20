'''from typing import List, Tuple, Optional, Callable
from data.data_loader import GlobalDataManager 
from algorithms.models import Schedule
from core.fitness import calculate_fitness
from config import PSO_ITERATIONS
import time
import random

def run_pso(data_manager: GlobalDataManager, base_assignments: List[Tuple], config: dict, ui_callback: Optional[Callable] = None) -> Schedule:
    """
    Hàm chạy PSO chính. TẠM THỜI CHƯA TRIỂN KHAI LOGIC, chỉ dùng để mô phỏng.
    """
    
    # 1. Khởi tạo một Schedule ban đầu (Dùng làm kết quả mô phỏng)
    initial_schedule = Schedule(base_assignments, data_manager)
    calculate_fitness(initial_schedule)
    
    # 2. Bắt đầu mô phỏng vòng lặp và gọi callback
    iterations = config.get('iterations', PSO_ITERATIONS)
    print(f"Bỏ qua logic PSO. Mô phỏng {iterations} vòng lặp...")
    
    mock_best_schedule = initial_schedule.clone()

    for i in range(1, iterations + 1):
        if ui_callback and i % 20 == 0:
            # Mô phỏng sự cải thiện
            time.sleep(0.01) 
            mock_best_schedule.fitness = mock_best_schedule.fitness * 1.05 + 10 
            mock_best_schedule.hard_violations = max(0, mock_best_schedule.hard_violations - 1)
            mock_best_schedule.soft_violations = max(0, mock_best_schedule.soft_violations - 1)

            ui_callback(i, iterations, mock_best_schedule)

    # 3. Trả về kết quả đã mô phỏng
    return mock_best_schedule'''
    
import random
from typing import List, Tuple, Optional, Callable
from data.data_loader import GlobalDataManager
from algorithms.models import Schedule
from core.fitness import calculate_fitness

def run_pso(data_manager: GlobalDataManager, base_assignments: List[Tuple], config: dict, ui_callback: Optional[Callable] = None) -> Schedule:
    """
    Thuật toán PSO thực tế sử dụng các hàm có sẵn để xếp lịch.
    """
    swarm_size = config.get('swarm_size', 50)
    iterations = config.get('iterations', 100)
    
    # 1. Khởi tạo bầy đàn (Swarm)
    swarm = [Schedule(base_assignments, data_manager) for _ in range(swarm_size)]
    for particle in swarm:
        calculate_fitness(particle)
        # Khởi tạo pbest ban đầu
        particle.pbest_assignments = [a.clone() for a in particle.assignments]
        particle.pbest_fitness = particle.fitness

    # Xác định gbest (Cá thể tốt nhất bầy đàn)
    gbest = max(swarm, key=lambda p: p.fitness).clone()

    # 2. Vòng lặp tối ưu hóa
    for i in range(1, iterations + 1):
        for particle in swarm:
            # "Bay" tới vị trí tốt hơn bằng cách học hỏi từ pbest và gbest
            # Thay vì tính vận tốc phức tạp, ta dùng xác suất thay đổi gene (Gene swap)
            for j in range(len(particle.assignments)):
                r = random.random()
                
                # Học hỏi từ gbest (Xác suất 40%)
                if r < 0.4:
                    particle.assignments[j].time_slot = gbest.assignments[j].time_slot
                    particle.assignments[j].room = gbest.assignments[j].room
                # Học hỏi từ pbest cá nhân (Xác suất 20%)
                elif r < 0.6:
                    particle.assignments[j].time_slot = particle.pbest_assignments[j].time_slot
                    particle.assignments[j].room = particle.pbest_assignments[j].room
                # Đột biến ngẫu nhiên để thoát khỏi tối ưu cục bộ (Xác suất 10%)
                elif r < 0.7:
                    particle.assignments[j].time_slot = random.choice(list(data_manager.time_slots))
                    particle.assignments[j].room = random.choice(list(data_manager.rooms))

            # Tính toán lại Fitness sau khi thay đổi vị trí
            calculate_fitness(particle)

            # Cập nhật PBest (Tốt nhất cá nhân)
            if particle.fitness > particle.pbest_fitness:
                particle.pbest_fitness = particle.fitness
                particle.pbest_assignments = [a.clone() for a in particle.assignments]

            # Cập nhật GBest (Tốt nhất bầy đàn)
            if particle.fitness > gbest.fitness:
                gbest = particle.clone()

        # Gửi dữ liệu về GUI để hiển thị tiến trình
        if ui_callback:
            ui_callback(i, iterations, gbest)

        # Nếu đã đạt kết quả hoàn hảo (0 lỗi) thì dừng sớm
        if gbest.hard_violations == 0 and gbest.soft_violations == 0:
            break

    return gbest