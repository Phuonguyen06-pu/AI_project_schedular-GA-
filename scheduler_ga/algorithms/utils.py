from typing import List, Tuple, Optional, Dict
from data.data_loader import Subject, Lecturer, Room, ClassGroup, GlobalDataManager 
import random

def select_suitable_room(class_group: ClassGroup, room_initial: Optional[Room], all_rooms: List[Room]) -> Optional[Room]:
    """Tìm phòng phù hợp nhất nếu phòng ban đầu không đủ sức chứa hoặc không đúng loại."""
    if room_initial is None:
        return None
        
    if room_initial.capacity >= class_group.student_count: # đủ sức chứa
        return room_initial
        
    suitable_rooms = [
        r for r in all_rooms
        if r.room_type == room_initial.room_type and r.capacity >= class_group.student_count
    ]  #lọc các phòng phù hợp

    if suitable_rooms:
        return min(suitable_rooms, key=lambda r: r.capacity) #chọn phòng có sức chứa nhỏ nhất đủ dùng
    return None

def generate_base_assignments(data_manager: GlobalDataManager) -> List[Tuple[Subject, ClassGroup, Lecturer]]:
    '''Sinh danh sách các nhiệm vụ cố định (Subject, ClassGroup, Lecturer). chỉ cần xếp giờ và phòng học'''
    assignments: List[Tuple[Subject, ClassGroup, Lecturer]] = []
    
    subject_to_lecturers: Dict[str, List[Lecturer]] = {}
    
    # gom nhóm gv theo môn họ có thể dạy
    for gv in data_manager.lecturers: 
        for mon_code in gv.subjects_can_teach:
            subject_to_lecturers.setdefault(mon_code, []).append(gv)

    # tạo danh sách cho môi lớp và môn học, chọn ngẫu nhiên gv phù hợp
    for cls in data_manager.class_groups:
        for sub in data_manager.subjects:
            gv_phu_hop = subject_to_lecturers.get(sub.code, [])
            
            if not gv_phu_hop: continue
                
            lecturer = random.choice(gv_phu_hop)
            assignments.append((sub, cls, lecturer))
            
    return assignments