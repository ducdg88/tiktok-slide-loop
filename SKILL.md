---
name: tiktok-slide-loop
description: >-
  Làm series ảnh chạy slide TikTok (Photo Mode, carousel dọc 9:16, 1080x1920) kéo khách về ducpt.com,
  rồi học liên tục theo vòng lặp: nạp vấn đề thị trường từ bình luận, tin nhắn, nghiên cứu, đo số liệu
  thật từng bài, chấm dạng nội dung và hook thắng hay thua, đề xuất lịch 7 bài kế tiếp. Dùng khi Founder nói
  "ảnh slide", "ảnh chạy slide", "carousel TikTok", "photo mode", "series AI báo cáo láo", "làm tập mới",
  "nhập số liệu TikTok", "báo cáo vòng lặp series", "vấn đề thị trường", "content 30 đến 90 ngày".
---

# TikTok Slide Loop: series ảnh 9:16 tự cải tiến

Mục tiêu: một bài mỗi ngày trong 30 đến 90 ngày, mỗi bài là 6 đến 8 ảnh dọc 9:16, kéo người xem về ducpt.com
(khóa "Doanh nghiệp một người": bài 1 và bài 6 miễn phí, còn lại premium). Kiểm tra danh mục thật bằng
MCP `ducpt_course_catalog` trước khi hứa nội dung khóa học.

## Luật cứng

- **Khung 1080x1920 (9:16).** Không đổi cỡ. Chữ quan trọng tránh 150px trên và 220px dưới (vùng giao diện TikTok che).
- **Không bịa.** Chuyện "AI báo cáo láo" phải là chuyện có thật của Founder hoặc từ bình luận thật. Số liệu trong hook chỉ dùng số thật.
- **Không dấu gạch dài** (en dash, em dash) trong mọi chữ trên slide, caption, báo cáo. Dùng dấu phẩy, hai chấm hoặc tách câu.
- **Học từ số thật.** Chưa có số liệu thì ghi `info_gap`, không đoán. Điểm chỉ tính từ lệnh `metrics` do Founder nhập (TikTok chưa nối API).
- **Không tự đăng.** Skill chỉ dựng ảnh, caption và kế hoạch. Founder đăng tay.
- **Mỗi slide một ý.** Đọc xong trong 2 đến 3 giây. Tối đa khoảng 20 chữ cho mỗi slide, trừ slide dạng danh sách.

## Giải phẫu một bài (khung 7 slide)

1. **Hook:** câu gây sốc hoặc đồng cảm + nhân vật robot "DONE". Quyết định người xem có vuốt tiếp không.
2. đến 5. **Thân:** mỗi slide một ý (kiểu `versus`: AI nói màu xanh, Sự thật màu đỏ; hoặc `list`, `text`).
6. **Cách trị** (`fix`, màu vàng): một luật duy nhất, người xem lưu lại được.
7. **CTA** (`cta`): bình luận từ khoá (LUẬT, AGENT...) và link ducpt.com.

## Chín dạng nội dung (mã dùng trong `--format`)

| Mã | Dạng |
|---|---|
| ai_bao_cao_lao | Kiểu lỗi AI khi code, báo xong mà chưa xong |
| cach_tri | Luật khắc chế, đi cặp với một tập báo cáo láo trước đó |
| ai_noi_vs_su_that | Meme 2 cột, dễ chia sẻ |
| truoc_sau | Giao việc kiểu thường so với kiểu Công ty 1 người |
| hau_truong | Một ngày vận hành công ty bằng agent, số thật |
| dap_hieu_lam | "AI thay lập trình viên?", "mua gói đắt là xong?" |
| giai_thich_1_slide | Agent, MCP, Loop, Context, Skill, Gate nói bằng tiếng người |
| checklist | Bài để lưu, làm quà đổi bình luận |
| thu_thach | Thử thách công khai 30 ngày, bám 10 bài của khóa |

Nhịp 90 ngày: ngày 1 đến 30 gây chú ý bằng nỗi đau, ngày 31 đến 60 tạo niềm tin bằng cách trị,
ngày 61 đến 90 chuyển đổi về ducpt.com. Vòng lặp được phép đổi tỉ lệ này khi số liệu chỉ ra.

## Quy trình làm một tập

Workspace mặc định `E:\TikTokSlides\ducpt` (đổi bằng biến `TIKTOK_SLIDE_WS`). Lần đầu: `python scripts/series.py init`.

1. **Chọn đề:** đọc báo cáo vòng lặp mới nhất trong `reports/` (nếu có) và `problems.json`. Ưu tiên vấn đề nhiều phiếu, chưa dùng.
2. **Viết kịch bản JSON** vào `episodes/epXX.json` theo mẫu `examples/ep01.json`.
   Kiểu slide: `hook`, `text`, `versus`, `fix`, `list`, `cta`. Bọc `**chữ**` để tô màu nhấn.
   Tuỳ chọn `"image": "<đường dẫn ảnh>"` ở từng slide để làm nền (ảnh AI tạo bằng skill `ai-multimodal`, không có chữ trong ảnh).
   `"theme": "terminal"` (nền tối, mặc định) hoặc `"light"`.
3. **Dựng ảnh:** `python scripts/render_slides.py <workspace>/episodes/epXX.json` ra `episodes/epXX/slide_01.png`...
4. **Tự kiểm bằng mắt:** mở vài PNG bằng Read. Kiểm chữ không tràn, không bị che ở vùng trên và dưới, đủ dấu tiếng Việt, không có dấu gạch dài.
5. **Viết caption:** 1 câu móc + 1 câu giá trị + CTA + 3 đến 5 hashtag (#congty1nguoi #AI #laptrinh #ducpt ...).
6. **Ghi nhật ký** khi Founder đăng:
   `series.py add-post --ep N --date YYYY-MM-DD --topic "..." --format <mã> --hook-type <kiểu> --hook "<câu hook>" --problem PXXX`

Kiểu hook (`--hook-type`): so_lieu_ca_nhan, cau_hoi_dau, phan_truc_giac, truoc_sau, loi_hua_nhanh, meme.

## Vòng lặp học (chạy mỗi 7 bài hoặc mỗi tuần)

1. **THỊ TRƯỜNG (nghiên cứu).** Mỗi vòng tìm ít nhất 3 vấn đề mới có nguồn thật:
   - Tìm web (WebSearch) theo các hướng: lỗi và sự cố AI coding agent mới nhất, khảo sát lập trình viên
     (Stack Overflow, Sonar...), bài than phiền trên Reddit, Hacker News, nhóm Facebook dev Việt, xu hướng
     TikTok photo mode, đối thủ cùng ngách (kênh dạy AI, "một người một công ty").
   - Nguồn nội bộ: bình luận TikTok, tin nhắn, câu hỏi học viên, danh mục bài ducpt.com (`ducpt_course_catalog`).
   - Ghi: `series.py add-problem --pain "..." --source research --evidence "<số liệu hoặc trích nguyên văn>" --url <link>`
   - Gặp lại vấn đề cũ: `series.py vote-problem --id PXXX --evidence "..." --url <link>` (thêm một phiếu).
   - Số liệu đưa lên slide phải lấy đúng từ nguồn, ghi `"source"` ở slide đó (hiện dòng "Nguồn:" nhỏ).
2. **NỘI DUNG.** Kho tập chưa đăng dưới 7 thì viết thêm kịch bản cho đủ 7, theo đề xuất của báo cáo, dựng ảnh, tự kiểm bằng mắt.
3. **ĐO.** Founder nhập số liệu sau 48 giờ (và 7 ngày nếu có):
   `series.py metrics --ep N --hours 48 --views .. --likes .. --comments .. --shares .. --saves .. --profile-views .. --link-clicks ..`
   Điểm = (lưu×3 + chia sẻ×3 + bình luận×2 + thích) / view × 100.
4. **CHẨN ĐOÁN + SỬA.** `series.py report --next 7` xếp hạng dạng và hook, đánh dấu THẮNG (từ 1,3 lần trung vị, đủ 3 bài)
   và THUA (dưới 0,5 lần trung vị), cập nhật điểm `hooks.json`, đề xuất 7 bài kế tiếp theo tỉ lệ 70/20/10
   (dạng thắng / biến thể / thử nghiệm mới), mỗi bài gắn một vấn đề thị trường.
5. **XÁC MINH TRƯỚC / SAU.** Mỗi lần `report` lưu một mốc vào `loops.json` và in bảng so với mốc trước:
   điểm trung bình 7 bài gần nhất, tỉ lệ bấm link, số bài có số liệu, số vấn đề trong kho.
   Không cải thiện 3 vòng liên tiếp thì báo cáo tự ghi ĐỔI GIẢ THUYẾT: đổi hẳn một biến (nhóm khách, kiểu hook,
   dạng chủ lực). Không nới cách đo.
6. **LẶP.** Quay lại bước 1.

Khi một bài lên xu hướng: làm ngay tập "phần 2" và tập `cach_tri` đi cặp, ghim bài đó, thêm từ khoá bình luận vào CTA.

## Chạy vòng lặp tự động

- Trong một phiên Claude Code: đặt lịch mỗi ngày (CronCreate, hết hạn sau 7 ngày) với lời nhắc
  "Chạy skill tiktok-slide-loop: nhịp thị trường, bổ sung kho tập đủ 7, chạy report, báo Founder info_gap".
- Việc Founder vẫn phải tự làm: đăng bài, nhập số liệu. Vòng lặp nhắc chứ không tự đăng.

## Báo cáo cho Founder

Ngắn gọn: tập đã dựng (đường dẫn thư mục PNG), caption, vấn đề đã dùng, các `info_gap` còn thiếu
(ví dụ "tập #03 chưa nhập số liệu"), và 7 bài đề xuất kế tiếp.
