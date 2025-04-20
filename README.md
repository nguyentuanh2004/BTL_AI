# BTL_AI
Bài tập lớn học phần Trí tuệ nhân tạo. Game cờ đam đơn giản với thuật toán Minimax cắt tỉa AlphaBeta.
# Mô tả
Game có hai chế độ chơi: chơi với người và chơi với AI. Game được viết bằng Python với thư viện Pygame và Pygame_menu bởi TuAnhcutenhatlopKHMT :>
# Tính năng
- **Hai chế độ chơi**: Đấu với AI hoặc hai người chơi
- **Ba cấp độ khó**: Easy, Medium, Hard với chế độ chơi với AI
- **Giao diện thân thiện**: Thiết kế đẹp mắt với màu hồng pastel là tone màu chủ đạo, siêu dễ thương :>
- **Tùy chọn người đi trước**
- **Hệ thống gợi ý**: Hỗ trợ người chơi với các nước đi khả thi
- **Âm thanh**: Nhạc nền có thể bật/tắt
- **Hiển thị số quân đã ăn**: Theo dõi trực quan tiến trình trận đấu
# Required Packages
- cài đặt Python 3.x trở lên
- pygame >= 2.1.0
- pygame-menu >= 4.2.0
# Install
`pip install pygame pygame-menu`
# Running the Game
Chạy file "Main.py" trong thư mục gốc
# Cách chơi
## 1. Chạy "Main.py" để khởi động trò chơi
## 2. Từ màn hình chính, chọn một trong số các tùy chọn
- ONE PLAYER: Chơi với AI
- TWO PLAYER: Chơi với người khác
- HOW TO PLAY: Xem hướng dẫn cách chơi
- OPTIONS: Điều chỉnh cài đặt (âm thanh, gợi ý)
- EXIT: Thoát trò chơi
## 3. Trong chế độ 1 người chơi
- Chọn ai sẽ đi trước (YOU/AI)
- Chọn độ khó (EASY/MEDIUM/HARD)
- Nhập tên người chơi
- Nhấn START GAME để bắt đầu
## 4. Trong chế độ 2 người chơi
- Chọn màu bắt đầu (PINK/BLUE)
- Nhập tên cho cả hai người chơi
- Nhấn START GAME để bắt đầu
# Luật chơi
- Quân cờ thường chỉ có thể di chuyển theo đường chéo về phía trước
- Bắt buộc phải ăn quân khi có thể
- Khi một quân cờ đến hàng cuối cùng, nó trở thành quân Vua và có thể di chuyển theo đường chéo theo cả hai hướng
- Người chơi thắng khi ăn hết quân của đối thủ hoặc đối thủ không còn nước đi hợp lệ
# Tác giả
Chill girls from Computer Science 63RD
