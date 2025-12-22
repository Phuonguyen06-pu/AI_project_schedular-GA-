```markdown
# 📅 Hệ Thống Tự Động Lập Lịch Giảng Dạy
### (Automated Academic Scheduler)

> **Giới thiệu:** Hệ thống cung cấp giải pháp tối ưu hóa bài toán lập lịch giảng dạy bằng cách sử dụng các thuật toán trí tuệ nhân tạo, bao gồm **Giải thuật Di truyền (Genetic Algorithm - GA)** và **Tối ưu hóa bầy đàn (Particle Swarm Optimization - PSO)**. Chương trình tự động phân bổ nguồn lực giữa giảng viên, môn học và phòng học nhằm thỏa mãn tối đa các ràng buộc trong môi trường giáo dục.

---

## 📂 Cấu trúc dự án

Dự án được tổ chức theo mô hình phân lớp để dễ dàng bảo trì và mở rộng:

| Thư mục / File | Mô tả chức năng |
| :--- | :--- |
| `algorithms/` | Chứa logic điều khiển các thuật toán tối ưu hóa (**GA**, **PSO**), các lớp mô hình đối tượng (`Assignment`, `Schedule`) và các hàm bổ trợ tính toán. |
| `core/` | Thành phần xử lý tính toán cốt lõi, bao gồm kiểm tra các ràng buộc (**constraints**) và hàm đánh giá độ thích nghi (**fitness**). |
| `data/` | Quản lý dữ liệu đầu vào dưới định dạng JSON và các lớp chịu trách nhiệm tải, chuẩn hóa dữ liệu (`GlobalDataManager`). |
| `ui/` | Giao diện người dùng đồ họa (**GUI**) phục vụ việc tương tác, cấu hình tham số và hiển thị kết quả trực quan. |
| `config.py` | Quản lý các tham số hệ thống, trọng số của hàm fitness và danh sách cấu hình nghiệp vụ. |
| `main.py` | Điểm khởi tạo và điều hướng chính của toàn bộ ứng dụng. |

---

## ⚙️ Yêu cầu cài đặt

Để vận hành hệ thống, môi trường máy tính cần cài đặt **Python 3.10** trở lên.

1. **Cài đặt thư viện:**
   Chạy lệnh sau để cài đặt các thư viện phụ thuộc:
   ```bash
   pip install -r requirements.txt

```

2. **Cấu hình dữ liệu:**
Đảm bảo file dữ liệu nguồn `data/data_input.json` đã được định cấu hình đúng thông tin về giảng viên và phòng học trước khi chạy.

---

## 🚀 Hướng dẫn thực thi chương trình

**Bước 1: Khởi chạy chương trình**
Chạy file thực thi chính từ thư mục gốc:

```bash
python main.py

```

**Bước 2: Thao tác trên giao diện (GUI)**

1. **Lựa chọn thuật toán:** Chọn thuật toán mục tiêu mong muốn (`GA` hoặc `PSO`).
2. **Thiết lập tham số:** Điều chỉnh các thông số vận hành như *Kích thước quần thể* và *Số lượng thế hệ lặp*.
3. **Thực thi:** Kích hoạt tiến trình tối ưu hóa và theo dõi kết quả lịch trình được trích xuất trực quan trên màn hình.

---

## 🧠 Cơ chế đánh giá (Fitness Scoring)

Hệ thống đánh giá chất lượng lịch trình dựa trên trọng số của hai nhóm chỉ số dưới đây:

### 🔴 Ràng buộc cứng (Hard Constraints)

*Bắt buộc phải thỏa mãn, nếu vi phạm lịch trình sẽ không hợp lệ.*

* Đảm bảo **không có sự xung đột** về thời gian của giảng viên.
* Đảm bảo sức chứa của phòng học phù hợp với lớp học.

### 🟢 Ràng buộc mềm (Soft Constraints)

*Tối ưu hóa để đạt điểm số cao nhất.*

* Tối ưu hóa dựa trên giờ cấm (giờ bận) của giảng viên.
* Ưu tiên phân bổ các môn học đặc thù vào các khung giờ và phòng học phù hợp nhất.

---

*Dự án được phát triển nhằm mục đích nghiên cứu và ứng dụng AI trong quản lý giáo dục.*

```

### Các điểm nhấn trong mẫu này:
1.  **Badges (Huy hiệu):** Thêm 3 cái huy hiệu ở đầu (Python, Algorithm, Status) nhìn rất "xịn".
2.  **Bảng (Table):** Phần cấu trúc dự án dùng bảng thay vì gạch đầu dòng giúp dễ nhìn hơn rất nhiều.
3.  **Code Blocks:** Các lệnh cài đặt và chạy được bỏ vào khung code để dễ copy.
4.  **Icon & Emoji:** Dùng `🔴` và `🟢` để phân biệt rõ ràng giữa ràng buộc cứng và mềm.

```