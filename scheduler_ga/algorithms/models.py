from data.data_loader import Subject, Lecturer, Room, ClassGroup, DetailedTimeSlot, GlobalDataManager # type: ignore
from typing import List, Tuple, Optional
import random

class Assignment:
    """Một Gene: Đại diện cho 1 dòng trong lịch trình, bao gồm môn học, lớp, giảng viên, phòng học và khung giờ."""

    def __init__(
        self,
        subject: Subject,
        class_group: ClassGroup,
        lecturer: Lecturer,
        room: Optional[Room] = None,
        time_slot: Optional[DetailedTimeSlot] = None,
    ) -> None:
        self.subject = subject
        self.class_group = class_group
        self.lecturer = lecturer
        self.room = room
        self.time_slot = time_slot

    def clone(self) -> "Assignment":
        return Assignment(
            self.subject, self.class_group, self.lecturer, 
            self.room, self.time_slot
        )

    def __repr__(self) -> str:
        tg_info = f"Thứ {self.time_slot.day}_{self.time_slot.session}" if self.time_slot else "N/A"
        return f"Assign({self.subject.code}/{self.class_group.code}, TG={tg_info})"

class Schedule:
    """Một Lịch trình: Đại diện cho một giải pháp hoàn chỉnh."""
    def __init__(self, base_assignments: List[Tuple], data_manager: GlobalDataManager) -> None:
        
        # khởi tạo quần thể từ danh sách nhiệm vụ cố định
        from algorithms.ga import generate_initial_assignments
        self.assignments: List[Assignment] = generate_initial_assignments(base_assignments, data_manager)

        self.fitness: float = 0.0
        self.hard_violations: int = 0
        self.soft_violations: int = 0
        
        # PSO
        self.pbest_assignments: List[Assignment] = [a.clone() for a in self.assignments]
        self.pbest_fitness: float = self.fitness


    def clone(self) -> "Schedule":
        """Tạo bản sao sâu của lịch trình."""
        new = Schedule.__new__(Schedule)
        new.assignments = [a.clone() for a in self.assignments]
        new.fitness = self.fitness
        new.hard_violations = self.hard_violations
        new.soft_violations = self.soft_violations
        if hasattr(self, 'pbest_assignments'):
            new.pbest_assignments = [a.clone() for a in self.pbest_assignments]
            new.pbest_fitness = self.pbest_fitness
        else:
            # Khởi tạo mặc định nếu không tồn tại (cho các cá thể mới sinh ra trong GA)
            new.pbest_assignments = []
            new.pbest_fitness = 0.0
        return new

    def __len__(self) -> int:
        return len(self.assignments)