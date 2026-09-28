# tiktok-slide-loop

**Tiếng Việt** | [English](#english)

Skill cho Claude Code làm series **ảnh chạy slide TikTok** (Photo Mode, dọc 9:16, 1080x1920) và tự cải tiến bằng vòng lặp học từ thị trường và số liệu thật. Đang dùng cho series "AI BÁO CÁO LÁO" của [ducpt.com](https://ducpt.com/?utm_source=github&utm_medium=readme&utm_campaign=tiktok-slide-loop).

- `scripts/render_slides.py`: kịch bản JSON thành bộ PNG 9:16, có logo chữ và chữ chìm thương hiệu, dòng ghi nguồn cho số liệu.
- `scripts/series.py`: kho vấn đề thị trường (có link nguồn), nhật ký bài, số liệu, báo cáo vòng lặp có so sánh trước / sau.
- `SKILL.md`: quy trình đầy đủ, 9 dạng nội dung, luật không bịa số liệu.

```bash
pip install playwright
python scripts/series.py init
python scripts/render_slides.py examples/ep01.json
python scripts/series.py report
```

Dữ liệu nằm ngoài repo (mặc định `E:\TikTokSlides\ducpt`, đổi bằng biến `TIKTOK_SLIDE_WS`).

---

## English

A Claude Code skill for producing a **TikTok photo carousel series** (Photo Mode, vertical 9:16, 1080x1920) that improves itself through a learning loop driven by market research and real post metrics. Used for the "AI BÁO CÁO LÁO" (AI lies in its reports) series of [ducpt.com](https://ducpt.com/?utm_source=github&utm_medium=readme&utm_campaign=tiktok-slide-loop).

- `scripts/render_slides.py`: JSON script to a set of 9:16 PNGs, with text logo, faint brand watermark and a source line for statistics.
- `scripts/series.py`: market problem bank (with source links), post log, metrics, and a loop report with before / after comparison.
- `SKILL.md`: full workflow, 9 content formats, and the no-made-up-numbers rule.

Data lives outside the repo (default `E:\TikTokSlides\ducpt`, override with `TIKTOK_SLIDE_WS`).

---

**Made by DUCPT.** Học cách vận hành Công ty 1 người với AI / Learn to run a one-person company with AI: [ducpt.com](https://ducpt.com/?utm_source=github&utm_medium=readme&utm_campaign=tiktok-slide-loop)

Giấy phép / License: [MIT](LICENSE)
