# F319 Forum Crawler — BDD Spec

## Feature Description

Ứng dụng web cho phép người dùng crawl (thu thập) dữ liệu bài viết của thành viên từ diễn đàn f319.com. Người dùng nhập user ID theo format `username.userid`, hệ thống sẽ tìm kiếm và trích xuất tất cả bài viết của thành viên đó, hỗ trợ xuất file CSV.

## User Stories

### US-1: Crawl bài viết của một thành viên
> **Là** một người phân tích dữ liệu chứng khoán,
> **Tôi muốn** nhập user ID của một thành viên f319 và lấy toàn bộ bài viết của họ,
> **Để** phân tích quan điểm và lịch sử đầu tư của thành viên đó.

### US-2: Crawl nhiều thành viên cùng lúc
> **Là** một nhà nghiên cứu,
> **Tôi muốn** nhập danh sách nhiều user IDs cùng lúc,
> **Để** thu thập dữ liệu hàng loạt và so sánh giữa các thành viên.

### US-3: Kiểm soát mức độ lấy nội dung
> **Là** người dùng,
> **Tôi muốn** chọn số lượng bài viết cần lấy full content (10, 20, 50, 100, hoặc tất cả),
> **Để** cân bằng giữa chất lượng dữ liệu và thời gian chờ.

### US-4: Theo dõi tiến trình real-time
> **Là** người dùng,
> **Tôi muốn** thấy tiến trình crawl đang diễn ra (đang xử lý user nào, bao nhiêu bài đã lấy),
> **Để** biết hệ thống đang hoạt động và ước lượng thời gian còn lại.

### US-5: Xuất kết quả ra CSV
> **Là** người phân tích,
> **Tôi muốn** tải file CSV chứa dữ liệu bài viết,
> **Để** mở bằng Excel hoặc import vào công cụ phân tích.

---

## Scenarios

### Scenario 1: Crawl thành công một user (Happy Path)

```gherkin
Given người dùng truy cập trang chủ của ứng dụng
When người dùng nhập "ngokha5566.713779" vào ô User ID
And người dùng nhấn nút "Crawl"
Then hệ thống hiển thị progress bar hoặc trạng thái "Đang crawl..."
And hệ thống tìm kiếm bài viết qua URL: /search/member?user_id=713779
And hệ thống lấy danh sách bài viết từ tất cả trang kết quả
And khi hoàn tất, hiển thị bảng kết quả với các cột:
  | Cột           | Mô tả                                    |
  |---------------|------------------------------------------|
  | STT           | Số thứ tự                                |
  | Tiêu đề       | Tên thread chứa bài viết                 |
  | Nội dung      | Content snippet hoặc full content        |
  | Ngày đăng     | Timestamp của bài viết                   |
  | Diễn đàn      | Tên subforum (vd: Thị trường chứng khoán)|
  | Link          | URL tới bài viết gốc trên f319.com       |
And hiển thị nút "Tải CSV"
```

### Scenario 2: Crawl nhiều users cùng lúc

```gherkin
Given người dùng truy cập trang chủ
When người dùng nhập "ngokha5566.713779, csdn.699927" vào ô User ID
And người dùng nhấn nút "Crawl"
Then hệ thống crawl lần lượt từng user
And hiển thị progress: "Đang xử lý user 1/2: ngokha5566..."
And khi hoàn tất, tạo 3 file CSV:
  | File                           | Nội dung                    |
  |--------------------------------|-----------------------------|
  | ngokha5566_713779_posts.csv    | Bài viết của ngokha5566     |
  | csdn_699927_posts.csv          | Bài viết của csdn           |
  | combined_posts.csv             | Tất cả bài viết gộp lại    |
And hiển thị thống kê cho từng user (số bài, thời gian crawl)
```

### Scenario 3: Chọn mức độ full content

```gherkin
Given người dùng đã nhập user ID
When người dùng chọn "20 posts" từ dropdown "Full Content"
And nhấn "Crawl"
Then hệ thống lấy snippet cho TẤT CẢ bài viết từ search results
And hệ thống lấy full content cho 20 bài viết MỚI NHẤT
And mỗi lần lấy full content, chờ 3 giây giữa các request
And bài viết full content được đánh dấu khác với snippet trong kết quả
```

### Scenario 4: User ID không hợp lệ (Error Path)

```gherkin
Given người dùng truy cập trang chủ
When người dùng nhập "invalid_user" (thiếu userid số)
And nhấn "Crawl"
Then hiển thị lỗi: "Format không hợp lệ. Vui lòng nhập theo format: username.userid (vd: ngokha5566.713779)"
And không thực hiện crawl
```

### Scenario 5: User không có bài viết

```gherkin
Given người dùng nhập user ID hợp lệ nhưng user không có bài viết
When nhấn "Crawl"
Then hệ thống hiển thị: "Không tìm thấy bài viết nào cho user này"
And không tạo file CSV
```

### Scenario 6: Lỗi kết nối mạng

```gherkin
Given người dùng nhập user ID hợp lệ
And kết nối tới f319.com bị timeout hoặc lỗi
When nhấn "Crawl"
Then hệ thống hiển thị lỗi: "Không thể kết nối tới f319.com. Vui lòng kiểm tra kết nối mạng."
And ghi chi tiết lỗi vào log file
```

### Scenario 7: Tải file CSV

```gherkin
Given crawl đã hoàn tất và có kết quả
When người dùng nhấn nút "Tải CSV"
Then trình duyệt download file CSV
And file CSV có encoding UTF-8 with BOM (mở được bằng Excel không bị lỗi tiếng Việt)
And file CSV chứa header row và tất cả bài viết
```

### Scenario 8: Bài viết quá dài — tự động skip full content

```gherkin
Given cấu hình SKIP_LONG_POSTS = True, LONG_POST_THRESHOLD = 5000
And đang crawl full content cho user có bài viết >5000 ký tự
Then hệ thống skip full content cho bài đó
And giữ snippet content thay thế
And ghi log: "Skipped post [id] - content too long (>5000 chars)"
```

### Scenario 9: Ô nhập liệu trống

```gherkin
Given người dùng truy cập trang chủ
When người dùng nhấn "Crawl" mà không nhập gì
Then hiển thị lỗi: "Vui lòng nhập ít nhất một User ID"
And ô nhập liệu được highlight màu đỏ
```

---

## Dữ liệu kỹ thuật từ f319.com

| Thành phần | URL Pattern | Ghi chú |
|------------|-------------|---------|
| User Profile | `/members/{username}.{userid}/` | Thông tin cơ bản + avatar |
| Tìm bài viết | `/search/member?user_id={userid}` | Redirect tới `/search/{search_id}/` |
| Phân trang | `/search/{search_id}/?page={n}` | ~20 posts/trang |
| Bài viết cụ thể | `/posts/{postid}/` | Redirect tới thread + anchor |
| Content selector | `.messageText.SelectQuoteContainer.ugc.baseHtml` | Trong thẻ `<article>` |

## Dữ liệu trích xuất từ search results

| Field | Selector / Location | Ví dụ |
|-------|---------------------|-------|
| Post Title | Link text trong kết quả | "DGC con hào kinh tế" |
| Content Snippet | Text dưới title | "dgc nó vẫn hoạt động bình thường chứ không phải..." |
| Author | "Đăng bởi: {username}" | ngokha5566 |
| Timestamp | Sau author | "Hôm nay, lúc 19:10" hoặc "52 phút trước" |
| Forum | "trong diễn đàn: {forum}" | Thị trường chứng khoán |
| Post ID | Từ URL trong link | 48099891 |

## Cấu hình

```python
# config.py
BASE_URL = "https://f319.com"
SEARCH_URL = f"{BASE_URL}/search/member"
POST_URL = f"{BASE_URL}/posts"

MAX_FULL_CONTENT_POSTS = 0     # 0 = tất cả, -1 = không lấy
FULL_CONTENT_DELAY = 3         # giây giữa các request
SKIP_LONG_POSTS = True
LONG_POST_THRESHOLD = 5000     # ký tự
REQUEST_TIMEOUT = 30           # giây
```
