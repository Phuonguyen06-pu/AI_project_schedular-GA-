from typing import List, Dict, Iterable
from algorithms.models import Schedule, Assignment 
from algorithms.helpers import check_time_overlap, check_lecturer_unavailable, _get_day_number, _normalize_string 
from config import MON_KHO_IDS 


def _index_assignments(schedule: Schedule):
    '''Gom các ca học theo GV / Lớp / Phòng để kiểm tra trùng lịch nhanh hơn'''
    
    events_by_lecturer, events_by_class, events_by_room = {}, {}, {}
    for assign in schedule.assignments:
        if assign.time_slot is None or assign.room is None: continue
        events_by_lecturer.setdefault(assign.lecturer.code, []).append(assign)
        events_by_class.setdefault(assign.class_group.code, []).append(assign)
        events_by_room.setdefault(assign.room.code, []).append(assign)
    return events_by_lecturer, events_by_class, events_by_room

def _count_collision(indexed_events: dict) -> int:
    '''đếm số ca học trùng nhau trong cùng 1 nhóm (GV/Lớp/Phòng)'''
    
    collision_count = 0
    for assignments in indexed_events.values():
        n = len(assignments)
        for i in range(n):
            for j in range(i + 1, n):
                if check_time_overlap(assignments[i].time_slot, assignments[j].time_slot):
                    collision_count += 1
    return collision_count

def count_hard_violations(schedule: Schedule) -> int:
    """Đếm tổng số vi phạm Ràng buộc Cứng (Hard Constraints)."""
    hard_violations = 0
    events_by_lecturer, events_by_class, events_by_room = _index_assignments(schedule)

    for assign in schedule.assignments:
        ts = assign.time_slot
        room = assign.room
        
        # HC Kiểm tra gán và tính hợp lệ đơn
        if ts is None or room is None: hard_violations += 5; continue  #chưa gán thời gian hoặc phòng
        if room.capacity < assign.class_group.student_count: hard_violations += 1  #sức chứa phòng không đủ
        if assign.subject.room_type_required and room.room_type != assign.subject.room_type_required: hard_violations += 1 #loại phòng không phù hợp
        if check_lecturer_unavailable(ts, assign.lecturer.unavailable_times): hard_violations += 1  #giảng viên bị trùng giờ cấm
             
    # HC Kiểm tra xung đột (Trùng lịch)
    hard_violations += _count_collision(events_by_lecturer) #GV dạy trùng giờ
    hard_violations += _count_collision(events_by_class)    #Lớp học trùng giờ
    hard_violations += _count_collision(events_by_room)     # Phòng học trùng giờ

    return hard_violations


def count_soft_violations(schedule: Schedule) -> int:
    """Đếm tổng số vi phạm Ràng buộc Mềm (Soft Constraints)."""
    soft_violations = 0
    for assign in schedule.assignments:
        if assign.time_slot is None: continue #chưa gán thời gian
        if assign.subject.code in MON_KHO_IDS: 
            if "SANG" not in _normalize_string(assign.time_slot.session): #Môn khó chỉ được xếp vào buổi sáng
                soft_violations += 1
    return soft_violations