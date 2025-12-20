import random
from typing import List, Tuple, Optional, Callable

from data.data_loader import GlobalDataManager
from algorithms.models import Schedule, Assignment 
from core.fitness import calculate_fitness
from config import GA_ELITISM_COUNT, GA_MUTATION_RATE, GA_POPULATION_SIZE, GA_GENERATIONS 
from algorithms.utils import generate_base_assignments, select_suitable_room 
from algorithms.helpers import check_lecturer_unavailable

def generate_initial_assignments(base_assignments: List[Tuple], data_manager: GlobalDataManager) -> List[Assignment]:
    """Tạo lịch trình ban đầu bằng cách gán ngẫu nhiên thời gian và phòng học cho các nhiệm vụ cố định."""
    assignments: List[Assignment] = []
    all_rooms = list(data_manager.rooms)
    all_time_slots = list(data_manager.time_slots)
    
    for sub, cls, lec in base_assignments:
        time_random = random.choice(all_time_slots) if all_time_slots else None

        # chọn random phòng, sau đó kiểm tra và điều chỉnh nếu không phù hợp
        room_random = random.choice(all_rooms) if all_rooms else None
        room_assigned = select_suitable_room(cls, room_random, all_rooms)

        assignments.append(Assignment(subject=sub,class_group=cls, lecturer=lec, room=room_assigned, time_slot=time_random,))
    return assignments


def initialize_population(data_manager: GlobalDataManager, population_size: int, base_assignments: Optional[List[Tuple]] = None) -> List[Schedule]:
    """Tạo quần thể ban đầu."""
    if base_assignments is None:
        base_assignments = generate_base_assignments(data_manager)

    population = [Schedule(base_assignments, data_manager) for _ in range(population_size)]
    return population



def selection_tournament(population: List[Schedule], num_parents: int, tournament_size: int = 3) -> List[Schedule]:
    """Chọn lọc Cha Mẹ"""
    if not population or num_parents <= 0: return []
    parents: List[Schedule] = []
    for _ in range(num_parents):
        candidates = random.sample(population, k=min(tournament_size, len(population)))
        best_candidate = max(candidates, key=lambda sch: sch.fitness)
        parents.append(best_candidate)
    return parents

def crossover_one_point(parent1: Schedule, parent2: Schedule) -> Schedule:
    """Lai ghép 1 điểm cắt (one-point crossover)."""
    n = min(len(parent1), len(parent2))
    if n <= 1: return parent1.clone() if len(parent1) > 0 else parent2.clone()
    cut = random.randint(1, n - 1)

    child = Schedule.__new__(Schedule)
    child.assignments = []

    for i in range(cut):
        child.assignments.append(parent1.assignments[i].clone())
    for i in range(cut, n):
        child.assignments.append(parent2.assignments[i].clone())

    child.fitness = 0.0
    child.hard_violations = 0
    child.soft_violations = 0
    
    # PSO 
    child.pbest_assignments = [a.clone() for a in child.assignments] 
    child.pbest_fitness = 0.0

    return child

def mutation_time_and_room(schedule: Schedule, data_manager: GlobalDataManager, mutation_rate: float) -> None:
    '''đột biến thời gian và phòng học cho một số lịch trình'''
    if mutation_rate <= 0.0: return
    all_rooms = list(data_manager.rooms)
    all_time_slots = list(data_manager.time_slots)

    for assign in schedule.assignments:
        if random.random() < mutation_rate:
            rand = random.random()
            
            # đột biến thời gian: chọn giờ gv không bận
            if rand < 0.5 and all_time_slots:
                # Lọc danh sách khung giờ trống của giảng viên
                suitable_slots = [ts for ts in all_time_slots 
                                 if not check_lecturer_unavailable(ts, assign.lecturer.unavailable_times)]
                assign.time_slot = random.choice(suitable_slots if suitable_slots else all_time_slots)
            # đột biến phòng học: chọn phòng đúng loại và đủ sức chứa
            elif all_rooms:
                suitable_rooms = [r for r in all_rooms 
                                 if r.room_type == assign.subject.room_type_required 
                                 and r.capacity >= assign.class_group.student_count]
                
                if suitable_rooms:
                    assign.room = random.choice(suitable_rooms)
                else:
                    room_random = random.choice(all_rooms)
                    assign.room = select_suitable_room(assign.class_group, room_random, all_rooms)

def run_ga(data_manager: GlobalDataManager, base_assignments: List[Tuple], config: dict, ui_callback: Optional[Callable] = None) -> Schedule:
    """
    Hàm chạy vòng lặp GA chính.
    """
    pop_size = config.get('pop_size', GA_POPULATION_SIZE)
    generations = config.get('generations', GA_GENERATIONS)
    mutation_rate = config.get('mutation_rate', GA_MUTATION_RATE)
    elitism_count = config.get('elitism_count', GA_ELITISM_COUNT)
    
    population = initialize_population(data_manager, pop_size, base_assignments)
    
    for individual in population:
        calculate_fitness(individual)

    best_overall = max(population, key=lambda sch: sch.fitness)

    for gen in range(1, generations + 1):
        population.sort(key=lambda x: x.fitness, reverse=True)
        best_now = population[0]

        if best_now.fitness > best_overall.fitness:
            best_overall = best_now.clone()

        if ui_callback and (gen % 10 == 0 or gen == 1 or best_now.fitness == best_overall.fitness):
            ui_callback(gen, generations, best_overall)

        if best_now.hard_violations == 0 and best_now.soft_violations == 0:
            best_overall = best_now.clone()
            break

        new_population: List[Schedule] = []
        new_population.extend(population[:elitism_count]) # Elitism

        while len(new_population) < pop_size:
            parents = selection_tournament(population, 2)
            if len(parents) < 2: break
            
            child = crossover_one_point(parents[0], parents[1])
            mutation_time_and_room(child, data_manager, mutation_rate)
            calculate_fitness(child)
            new_population.append(child)

        population = new_population

    if ui_callback:
        ui_callback(generations, generations, best_overall)
        
    return best_overall