from typing import Optional, Iterable, Tuple, List
import re
import unicodedata

from data.data_loader import DetailedTimeSlot 

def _normalize_string(s: str) -> str:
    """Chuẩn hóa chuỗi: in hoa, bỏ dấu."""
    if s is None: return ""
    s = str(s).upper()
    return "".join(
        ch for ch in unicodedata.normalize("NFD", s)
        if unicodedata.category(ch) != "Mn"
    )

def _get_day_number(day_value) -> Optional[int]:
    """Trích xuất số thứ trong tuần."""
    if day_value is None: return None
    if isinstance(day_value, int): return day_value
    m = re.search(r'\d+', str(day_value))
    return int(m.group()) if m else None

def parse_unavailable_token(token: List) -> Optional[Tuple]:
    """Phân tích chuỗi giờ cấm (từ list trong JSON) thành tuple có thể so sánh."""
    if not token or not isinstance(token, list): return None
    
    # Gộp list thành chuỗi và chuẩn hóa (VD: ["THỨ 2", "SÁNG"] -> "THU 2 SANG")
    full_str = _normalize_string(" ".join(map(str, token)))
    
    day = _get_day_number(full_str)
    
    # Xác định buổi
    session = None
    if "SANG" in full_str: session = "SANG"
    elif "CHIEU" in full_str: session = "CHIEU"
    
    if day is not None and session is not None:
        return ("SESSION", day, session)
    return None

def check_time_overlap(ts1: DetailedTimeSlot, ts2: DetailedTimeSlot) -> bool:
    """Kiểm tra 2 khung thời gian có trùng nhau không."""
    # Nếu cùng Thứ và cùng Buổi (Sáng/Chiều) thì là trùng
    return ts1.day == ts2.day and ts1.session == ts2.session

def check_lecturer_unavailable(time_slot: DetailedTimeSlot, unavailable_times: Iterable[List]) -> bool:
    """Kiểm tra slot thời gian có rơi vào giờ cấm của giảng viên không."""
    day_ts = _get_day_number(time_slot.day)
    session_ts = _normalize_string(time_slot.session)

    for raw in unavailable_times:
        parsed = parse_unavailable_token(raw)
        if not parsed: continue

        kind = parsed[0]

        if kind == "SESSION":
            _, day, session = parsed
            # Nếu trùng cả Thứ và Buổi (SANG/CHIEU) thì trả về True (Bận)
            if day_ts == day and session in session_ts: 
                return True 

    return False