from algorithms.models import Schedule 
from core.constraints import count_hard_violations, count_soft_violations 
from config import PHAT_CUNG, PHAT_MEM, BASE_FITNESS_SCORE 

def calculate_fitness(schedule: Schedule) -> float:
    """
    Tính toán và cập nhật Fitness, số vi phạm Cứng và Mềm cho lịch trình.
    
    Công thức: Fitness = BASE_SCORE - (PHAT_CUNG * HC_Violations + PHAT_MEM * SC_Violations)
    """
    
    #Đếm vi phạm
    hard_violations = count_hard_violations(schedule)
    soft_violations = count_soft_violations(schedule)

    # Tính toán điểm Fitness
    total_penalty = (PHAT_CUNG * hard_violations) + (PHAT_MEM * soft_violations)
    
    # Điểm Fitness cơ sở (BASE_FITNESS_SCORE * N_ASSIGNMENTS)
    base_score = BASE_FITNESS_SCORE * len(schedule.assignments)
    fitness = base_score - total_penalty

    # Cập nhật kết quả vào cá thể
    schedule.fitness = fitness
    schedule.hard_violations = hard_violations
    schedule.soft_violations = soft_violations

    return fitness