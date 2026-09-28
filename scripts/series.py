"""Vòng lặp học của series ảnh slide TikTok.

Dữ liệu nằm ở thư mục workspace (mặc định E:\\TikTokSlides\\ducpt):
    problems.json   kho vấn đề thị trường (nỗi đau khách), có nguồn và số phiếu
    posts.jsonl     mỗi dòng một bài đã đăng + số liệu đo thật
    hooks.json      thư viện hook, tự cập nhật điểm sau mỗi lần report
    reports/        báo cáo mỗi nhịp học
    loops.json      mốc chỉ số từng vòng để so trước / sau

Lệnh:
    series.py init
    series.py add-problem --pain "..." --source comment|research|lesson|dm|founder --evidence "..." [--url ...] [--format ai_bao_cao_lao]
    series.py vote-problem --id P003 [--n 1] [--evidence "..."]
    series.py add-post --ep 1 --date 2026-09-29 --topic "..." --format ai_bao_cao_lao --hook-type so_lieu_ca_nhan --hook "..." --slides 7 [--problem P001] [--url ...]
    series.py metrics --ep 1 --hours 48 --views 1200 --likes 80 --comments 12 --shares 5 --saves 30 [--profile-views 40] [--link-clicks 6] [--finish-rate 0.35]
    series.py report [--next 7]
"""
import argparse
import datetime as dt
import json
import os
import pathlib
import statistics
import sys

sys.stdout.reconfigure(encoding="utf-8")
WS = pathlib.Path(os.environ.get("TIKTOK_SLIDE_WS", r"E:\TikTokSlides\ducpt"))

FORMATS = {
    "ai_bao_cao_lao": "AI báo cáo láo (kiểu lỗi AI khi code)",
    "cach_tri": "Cách trị (luật khắc chế)",
    "ai_noi_vs_su_that": "AI nói vs Sự thật (meme 2 cột)",
    "truoc_sau": "Trước / Sau",
    "hau_truong": "Hậu trường vận hành công ty 1 người",
    "dap_hieu_lam": "Đập tan hiểu lầm",
    "giai_thich_1_slide": "Giải thích 1 slide (thuật ngữ)",
    "checklist": "Checklist / mẫu prompt để lưu",
    "thu_thach": "Thử thách công khai 30 ngày",
}
MIN_SAMPLES = 3  # số bài tối thiểu để kết luận một dạng thắng hay thua


def load_json(name, default):
    f = WS / name
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else default


def save_json(name, data):
    (WS / name).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_posts():
    f = WS / "posts.jsonl"
    if not f.exists():
        return []
    return [json.loads(x) for x in f.read_text(encoding="utf-8").splitlines() if x.strip()]


def save_posts(posts):
    (WS / "posts.jsonl").write_text("".join(json.dumps(p, ensure_ascii=False) + "\n" for p in posts), encoding="utf-8")


def score(m):
    """Điểm tương tác có trọng số trên 100 view. Lưu và chia sẻ nặng nhất vì TikTok ưu tiên."""
    v = m.get("views") or 0
    if v <= 0:
        return None
    raw = m.get("saves", 0) * 3 + m.get("shares", 0) * 3 + m.get("comments", 0) * 2 + m.get("likes", 0)
    return round(raw / v * 100, 2)


def cmd_init(a):
    for d in ("", "episodes", "reports"):
        (WS / d).mkdir(parents=True, exist_ok=True)
    for name, default in (("problems.json", []), ("hooks.json", [])):
        if not (WS / name).exists():
            save_json(name, default)
    (WS / "posts.jsonl").touch()
    print(f"Workspace sẵn sàng: {WS}")


def cmd_add_problem(a):
    probs = load_json("problems.json", [])
    pid = f"P{len(probs)+1:03d}"
    probs.append({"id": pid, "pain": a.pain, "source": a.source, "evidence": [a.evidence] if a.evidence else [],
                  "votes": 1, "format": a.format, "urls": [a.url] if a.url else [], "used_eps": [], "added": dt.date.today().isoformat()})
    save_json("problems.json", probs)
    print(f"Đã thêm {pid}: {a.pain}")


def cmd_vote_problem(a):
    probs = load_json("problems.json", [])
    for p in probs:
        if p["id"] == a.id:
            p["votes"] += a.n
            if a.evidence:
                p["evidence"].append(a.evidence)
            if a.url:
                p.setdefault("urls", []).append(a.url)
            save_json("problems.json", probs)
            print(f"{a.id} giờ có {p['votes']} phiếu")
            return
    sys.exit(f"Không thấy {a.id}")


def cmd_add_post(a):
    if a.format not in FORMATS:
        sys.exit(f"format phải là một trong: {', '.join(FORMATS)}")
    posts = load_posts()
    if any(p["ep"] == a.ep for p in posts):
        sys.exit(f"Tập {a.ep} đã có trong nhật ký")
    posts.append({"ep": a.ep, "date": a.date, "topic": a.topic, "format": a.format, "hook_type": a.hook_type,
                  "hook": a.hook, "slides": a.slides, "problem": a.problem, "url": a.url, "metrics": []})
    save_posts(posts)
    if a.problem:
        probs = load_json("problems.json", [])
        for p in probs:
            if p["id"] == a.problem and a.ep not in p["used_eps"]:
                p["used_eps"].append(a.ep)
        save_json("problems.json", probs)
    hooks = load_json("hooks.json", [])
    if a.hook and not any(h["text"] == a.hook for h in hooks):
        hooks.append({"text": a.hook, "type": a.hook_type, "eps": [a.ep], "score": None})
        save_json("hooks.json", hooks)
    print(f"Đã ghi tập #{a.ep:02d}")


def cmd_metrics(a):
    posts = load_posts()
    for p in posts:
        if p["ep"] == a.ep:
            m = {k: getattr(a, k) for k in ("views", "likes", "comments", "shares", "saves",
                                            "profile_views", "link_clicks", "finish_rate") if getattr(a, k) is not None}
            m["hours_after"] = a.hours
            m["measured_at"] = dt.datetime.now().isoformat(timespec="minutes")
            p["metrics"].append(m)
            save_posts(posts)
            print(f"Tập #{a.ep:02d} sau {a.hours}h: điểm {score(m)}")
            return
    sys.exit(f"Chưa có tập {a.ep}, chạy add-post trước")


def latest(p):
    """Lấy lần đo gần 48h nhất để các bài so sánh công bằng."""
    if not p["metrics"]:
        return None
    return min(p["metrics"], key=lambda m: abs(m.get("hours_after", 48) - 48))


def group(posts, key):
    g = {}
    for p in posts:
        m = latest(p)
        s = score(m) if m else None
        if s is not None:
            g.setdefault(p.get(key) or "?", []).append(s)
    return {k: {"n": len(v), "avg": round(statistics.mean(v), 2)} for k, v in g.items()}


def cmd_report(a):
    posts = load_posts()
    probs = load_json("problems.json", [])
    hooks = load_json("hooks.json", [])
    today = dt.date.today().isoformat()
    L = [f"# Báo cáo vòng lặp series, {today}", ""]

    measured = [p for p in posts if latest(p) and score(latest(p)) is not None]
    gaps = [p for p in posts if not latest(p)]
    L += ["## 1. ĐO", f"- Bài đã đăng: {len(posts)}, đã có số liệu: {len(measured)}"]
    if gaps:
        L.append(f"- info_gap: chưa có số liệu cho tập {', '.join('#%02d' % p['ep'] for p in gaps)}. Nhập bằng lệnh `metrics`, không đoán.")
    if measured:
        views = sum(latest(p).get("views", 0) for p in measured)
        clicks = sum(latest(p).get("link_clicks", 0) or 0 for p in measured)
        prof = sum(latest(p).get("profile_views", 0) or 0 for p in measured)
        L.append(f"- Tổng view: {views:,}, xem hồ sơ: {prof:,}, bấm link: {clicks:,}"
                 + (f", tỉ lệ bấm link/view: {clicks/views*100:.2f}%" if views else ""))
        L += ["", "| Tập | Dạng | Hook | View | Lưu | Chia sẻ | Điểm |", "|---|---|---|---|---|---|---|"]
        for p in sorted(measured, key=lambda x: -score(latest(x))):
            m = latest(p)
            L.append(f"| #{p['ep']:02d} | {p['format']} | {p.get('hook','')[:40]} | {m.get('views',0):,} | {m.get('saves',0)} | {m.get('shares',0)} | {score(m)} |")

    L += ["", "## 2. CHẨN ĐOÁN"]
    by_fmt = group(posts, "format")
    by_hook = group(posts, "hook_type")
    winners, losers = [], []
    if by_fmt:
        med = statistics.median(v["avg"] for v in by_fmt.values())
        L.append(f"- Điểm trung vị theo dạng: {med}")
        for k, v in sorted(by_fmt.items(), key=lambda x: -x[1]["avg"]):
            verdict = "chưa đủ mẫu"
            if v["n"] >= MIN_SAMPLES:
                if v["avg"] >= med * 1.3:
                    verdict = "THẮNG, nhân bản"; winners.append(k)
                elif v["avg"] < med * 0.5:
                    verdict = "THUA, tạm dừng hoặc đổi góc"; losers.append(k)
                else:
                    verdict = "giữ"
            L.append(f"  - {k}: {v['avg']} điểm, {v['n']} bài, {verdict}")
    if by_hook:
        L.append("- Theo kiểu hook: " + ", ".join(f"{k} {v['avg']} ({v['n']})" for k, v in sorted(by_hook.items(), key=lambda x: -x[1]["avg"])))
    if not by_fmt:
        L.append("- info_gap: chưa có bài nào có số liệu, chưa chẩn đoán được.")

    # cập nhật điểm hook từ số thật
    ep_score = {p["ep"]: score(latest(p)) for p in measured}
    for h in hooks:
        s = [ep_score[e] for e in h.get("eps", []) if ep_score.get(e) is not None]
        h["score"] = round(statistics.mean(s), 2) if s else None
    save_json("hooks.json", hooks)

    L += ["", "## 3. SỬA: đề xuất lịch kế tiếp", f"Phân bổ {a.next} bài: 70% dạng thắng, 20% biến thể, 10% thử nghiệm mới."]
    posted = {p["ep"] for p in posts}
    drafts = []
    for f in sorted((WS / "episodes").glob("ep*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        if d.get("episode") not in posted:
            drafts.append(d)
    planned = {d.get("problem") for d in drafts if d.get("problem")}
    if drafts:
        L.append(f"- Kho tập đã dựng, chưa đăng: {len(drafts)} tập (" + ", ".join("#%02d" % d["episode"] for d in drafts) + "). Đăng hết kho này trước khi dựng thêm.")
    fresh = sorted([p for p in probs if not p["used_eps"] and p["id"] not in planned], key=lambda p: -p["votes"])
    reuse = sorted([p for p in probs if p["used_eps"] or p["id"] in planned], key=lambda p: -p["votes"])
    tried = set(by_fmt)
    untried = [f for f in FORMATS if f not in tried]
    n_win = round(a.next * 0.7) if winners else 0
    plan = []
    pool = iter(fresh + reuse)
    for i in range(a.next):
        if i < n_win:
            fmt, why = winners[i % len(winners)], "dạng thắng"
        elif untried and i == a.next - 1:
            fmt, why = untried[0], "thử nghiệm dạng chưa chạy"
        else:
            cands = [f for f in FORMATS if f not in losers]
            fmt, why = cands[i % len(cands)], "biến thể / xoay vòng"
        prob = next(pool, None)
        plan.append((fmt, why, prob))
    for i, (fmt, why, prob) in enumerate(plan, 1):
        ptxt = f"{prob['id']} \"{prob['pain']}\" ({prob['votes']} phiếu, nguồn {prob['source']}{', đã có tập, làm góc mới' if prob in reuse else ''})" if prob else "info_gap: kho vấn đề đã cạn, cần nạp thêm từ bình luận hoặc nghiên cứu"
        L.append(f"{i}. [{fmt}] {why}. Vấn đề: {ptxt}")
    top_hooks = sorted([h for h in hooks if h["score"] is not None], key=lambda h: -h["score"])[:5]
    if top_hooks:
        L += ["", "Hook tốt nhất để tái dùng cấu trúc:"] + [f"- ({h['score']}) {h['text']}" for h in top_hooks]

    L += ["", "## 4. XÁC MINH: trước / sau"]
    loops = load_json("loops.json", [])
    loops = [x for x in loops if x["date"] != today]
    recent = sorted(measured, key=lambda p: p["ep"])[-7:]
    snap = {
        "date": today,
        "posts": len(posts),
        "measured": len(measured),
        "avg_last7": round(statistics.mean(score(latest(p)) for p in recent), 2) if recent else None,
        "click_rate": None,
        "problems": len(probs),
        "problems_fresh": len(fresh),
        "drafts": len(drafts),
        "winners": winners,
        "losers": losers,
        "stuck": 0,
    }
    rv = sum(latest(p).get("views", 0) for p in recent)
    if rv:
        snap["click_rate"] = round(sum(latest(p).get("link_clicks", 0) or 0 for p in recent) / rv * 100, 3)
    prev = loops[-1] if loops else None
    if prev is None:
        L.append("- Vòng đầu tiên, chưa có mốc trước để so. Mốc này được lưu làm \"trước\" cho vòng sau.")
    else:
        L += [f"| Chỉ số | Trước ({prev['date']}) | Sau ({today}) |", "|---|---|---|"]
        for k, name in (("avg_last7", "Điểm TB 7 bài gần nhất"), ("click_rate", "Tỉ lệ bấm link %"), ("measured", "Bài có số liệu"), ("problems", "Vấn đề thị trường trong kho")):
            L.append(f"| {name} | {prev.get(k)} | {snap.get(k)} |")
        if snap["avg_last7"] is None or prev.get("avg_last7") is None:
            snap["stuck"] = prev.get("stuck", 0)
            L.append("- info_gap: thiếu điểm ở một trong hai mốc, chưa kết luận cải thiện.")
        elif snap["avg_last7"] > prev["avg_last7"]:
            L.append(f"- CẢI THIỆN: điểm tăng {snap['avg_last7'] - prev['avg_last7']:+.2f}. Giữ hướng hiện tại.")
        else:
            snap["stuck"] = prev.get("stuck", 0) + 1
            L.append(f"- KHÔNG CẢI THIỆN ({snap['stuck']} vòng liên tiếp).")
            if snap["stuck"] >= 3:
                L.append("- ĐỔI GIẢ THUYẾT: 3 vòng không lên. Vòng tới đổi hẳn một biến: nhóm khách, kiểu hook hoặc dạng chủ lực. Không nới cách đo.")
    loops.append(snap)
    save_json("loops.json", loops)
    L += ["", "## 5. LẶP", "- Nạp vấn đề mới từ bình luận và tin nhắn tuần này (`add-problem`, `vote-problem`), rồi chạy lại `report` sau 7 bài."]

    out = WS / "reports" / f"loop-{today}.md"
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    print(f"\n[Đã lưu] {out}")


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    sp.add_parser("init")
    p = sp.add_parser("add-problem"); p.add_argument("--pain", required=True); p.add_argument("--source", required=True, choices=["comment", "research", "lesson", "dm", "founder"]); p.add_argument("--evidence"); p.add_argument("--format"); p.add_argument("--url")
    p = sp.add_parser("vote-problem"); p.add_argument("--id", required=True); p.add_argument("--n", type=int, default=1); p.add_argument("--evidence"); p.add_argument("--url")
    p = sp.add_parser("add-post")
    for k in ("date", "topic", "format", "hook-type", "hook"):
        p.add_argument("--" + k, required=True)
    p.add_argument("--ep", type=int, required=True); p.add_argument("--slides", type=int, default=7); p.add_argument("--problem"); p.add_argument("--url")
    p = sp.add_parser("metrics"); p.add_argument("--ep", type=int, required=True); p.add_argument("--hours", type=int, default=48)
    for k in ("views", "likes", "comments", "shares", "saves", "profile-views", "link-clicks"):
        p.add_argument("--" + k, type=int)
    p.add_argument("--finish-rate", type=float)
    p = sp.add_parser("report"); p.add_argument("--next", type=int, default=7)
    a = ap.parse_args()
    if a.cmd != "init" and not WS.exists():
        sys.exit(f"Chưa có workspace {WS}, chạy init trước")
    {"init": cmd_init, "add-problem": cmd_add_problem, "vote-problem": cmd_vote_problem, "add-post": cmd_add_post,
     "metrics": cmd_metrics, "report": cmd_report}[a.cmd](a)


if __name__ == "__main__":
    main()
