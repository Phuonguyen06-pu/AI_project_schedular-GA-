import json
from typing import List, Optional

class Subject:
    """Môn học"""
    def __init__(self, code, name, weekly_periods, room_type_required):
        self.code: str = code                               # mã môn
        self.name: str = name                               # tên môn
        self.weekly_periods: int = weekly_periods           # số buổi/tuần
        self.room_type_required: str = room_type_required   # loại phòng yêu cầu (VD: "LAB", "LT")

    def __repr__(self):
        return f"Môn: ({self.name}, Sô buổi: {self.weekly_periods}, Tiết: {self.room_type_required})"


class Lecturer:
    """Giảng viên"""
    def __init__(self, code, name, subjects_can_teach, unavailable_times):
        self.code: str = code                                      # mã gv
        self.name: str = name                                      # tên gv
        self.subjects_can_teach: List[str] = subjects_can_teach    # danh sách mã môn gv có thể dạy
        self.unavailable_times: List[list] = unavailable_times     # thời gian gv không thể dạy

    def __repr__(self):
        return f"Mã giảng viên: ({self.code}, Tên giảng viên: {self.name})"


class Room:
    """Phòng học"""
    def __init__(self, code, capacity, room_type):
        self.code: str = code                   # mã phòng
        self.capacity: int = capacity           # sức chứa
        self.room_type: str = room_type         # loại phòng 

    def __repr__(self):
        return f"Phòng {self.code}, Sức chứa:{self.capacity}SV, Loại phòng: {self.room_type}"


class ClassGroup:
    """Lớp"""
    def __init__(self, code, student_count):
        self.code: str = code                   # mã lớp
        self.student_count: int = student_count # sĩ số

    def __repr__(self):
        return f"Lớp {self.code}, Sĩ số: {self.student_count}"


class DetailedTimeSlot:
    """thời gian chi tiết"""
    def __init__(self, day: int, session: str):
        self.day: int = day                     # thứ trong tuần (2-7)
        self.session: str = session             # ca (SÁNG/CHIỀU)    

    def __repr__(self):
        buoi = "Sáng" if self.session == "SANG" else "Chiều"
        return f"Thứ {self.day} ({buoi})"



class GlobalDataManager:
    """Chứa và quản lý toàn bộ dữ liệu sau khi tải."""
    subjects: List[Subject] = []
    lecturers: List[Lecturer] = []
    rooms: List[Room] = []
    class_groups: List[ClassGroup] = []
    time_slots: List[DetailedTimeSlot] = [] 

    @classmethod
    def clear(cls):
        cls.subjects.clear()
        cls.lecturers.clear()
        cls.rooms.clear()
        cls.class_groups.clear()
        cls.time_slots.clear()
        
    @classmethod
    def _generate_standard_time_slots(cls) -> List[DetailedTimeSlot]:
        """Tạo ra các slot thời gian"""
        slots = []
        for day in range(2, 8):
            slots.append(DetailedTimeSlot(day, "SANG"))
            slots.append(DetailedTimeSlot(day, "CHIEU"))
        return slots


    @classmethod
    def load_data(cls, filepath: str):
        """Tải và chuẩn hóa dữ liệu từ file JSON."""
        cls.clear()
        
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        # 1. Load Subject (dạng: [Mã, Tên, Tiết, Loại Phòng])
        for m in data.get("MON", []):
            cls.subjects.append(Subject(m[0], m[1], int(m[2]), m[3]))

        # 2. Load Lecturer (dạng: [Mã, Tên, [Môn Dạy], [Giờ Cấm]])
        for g in data.get("GV", []):
            cls.lecturers.append(Lecturer(g[0], g[1], g[2], g[3]))

        # 3. Load Room (dạng: [Mã, Sức chứa, Loại])
        for p in data.get("PHONG", []):
            cls.rooms.append(Room(p[0], int(p[1]), p[2]))

        # 4. Load ClassGroup (dạng: [Mã, Sĩ số])
        for l in data.get("LOP", []):
            cls.class_groups.append(ClassGroup(l[0], int(l[1])))

        # 5. Chuẩn hóa TimeSlot
        cls.time_slots = cls._generate_standard_time_slots()
        
        return cls