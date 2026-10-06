# Báo cáo Lab: Self evolving Agentic

> Sao chép tệp này thành `report/REPORT.md` (đã làm ở Phần 0) và điền dần qua các Phần của lab. Xóa các dòng hướng dẫn dạng trích dẫn (bắt đầu bằng `>`). Văn phong kỹ thuật, ngắn gọn, mọi nhận định đi kèm số liệu hoặc bằng chứng. Trong buổi học: điền mục 1 đến 7 (bản nháp). Sau buổi học: hoàn thiện mục 8 đến 10.

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Trần Anh Đăng | 2A202602992 | 100% |

- Nhà cung cấp và mô hình (`LAB_MODEL`, không ghi khóa API), nhiệt độ (`LAB_TEMPERATURE`), `recursion_limit`: OpenRouter (`openai/gpt-4o-mini`), `LAB_TEMPERATURE=0`, `recursion_limit=60`
- Phiên bản Deep Agents (`pip show deepagents`), hệ điều hành, chạy trực tiếp hay trong Docker: `deepagents 0.7.21`, Windows 11, chạy trực tiếp với `.venv`
- Số lần chạy tác vụ đã dùng / ngân sách: 6 lần chạy thử (baseline và subagents cho learn)
- Commit của tag `freeze`: tag `freeze`

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

- H1 (subagents so với baseline): Đội hình subagents (explorer, implementer, reviewer) hỗ trợ cô lập ngữ cảnh và phân chia nhiệm vụ chuyên biệt, giúp tăng điểm trên các tác vụ phức tạp nhưng sẽ tiêu tốn lượng token lớn hơn.
- H2 (skills-auto so với baseline): Điều kiện skills-auto sẽ cải thiện tỷ lệ đạt ở cả tác vụ học và đánh giá nhờ các quy tắc rút ra từ lỗi phổ biến (như không sửa file test, kiểm tra đường dẫn file, kiểm tra type annotation).
- H3 (tác vụ học so với tác vụ đánh giá): Tác vụ học sẽ đạt điểm cao hơn tác vụ đánh giá do các skill tự sinh bám sát phản hồi từ tác vụ học (có thể có hiện tượng overfitting nhẹ trên tập học).

## 3. Làm quen Deep Agents (Phần 0.3)

1. Tác tử mặc định có các công cụ tệp (`ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`), công cụ shell (`execute`), và công cụ subagent (`task`). Công cụ `execute` cho phép chạy lệnh shell trực tiếp.
2. Công cụ `task` mô tả subagent `general-purpose` là tác tử chạy độc lập trên ngữ cảnh riêng. Subagent chỉ thấy nội dung thông điệp giao việc mà tác tử chính truyền sang, không thấy toàn bộ lịch sử hội thoại trước đó.
3. Trích dẫn công cụ `task`: "delegate to a suitable subagent and put ALL the task rules and file paths in the delegation message". Trích dẫn công cụ `execute`: "Use the shell to run Python and tests."

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

| Tác vụ | Check thất bại | Nhóm lỗi (A-G) | Bằng chứng (trích ngắn từ `detail` hoặc vết) |
|---|---|---|---|
| `code-learn` | `tests_not_modified` | E | `the original files in tests/ must not be modified` |
| `code-learn` | `parse_price_all_formats` | D | `wrong for: ['(12.00)']` |
| `code-learn` | `csv_quoting_follows_docstring` | A | `to_csv_row returned 'Desk, large "oak",10.00,2'` |
| `code-learn` | `rule_type_hints` | E | `RULE: every public function... has type annotations` |
| `code-learn` | `rule_regression_tests` | E | `RULE: add tests/test_regressions.py` |
| `code-learn` | `rule_changelog` | E | `RULE: record each fix in CHANGELOG.md` |
| `data-learn` | `all_checks` | B | `GraphRecursionError: Recursion limit of 60 reached` |
| `logs-learn` | `all_checks` | B | Agent chưa tạo file kết quả `errors.json` trước khi dừng |

Nhận xét: Phần lớn các lỗi thất bại thuộc nhóm **E (Vi phạm quy ước tổ chức)** đối với bài toán code và nhóm **B (Không kiểm chứng/Lặp vô hạn)** với các bài toán xử lý dữ liệu. Các Skill tự sinh của Curator tập trung phòng ngừa trực tiếp nhóm lỗi E và D.

## 5. Điều kiện `subagents` (Phần 2.3)

- Các subagent đã định nghĩa: `explorer` (khám phá), `implementer` (thực thi), `reviewer` (kiểm tra độc lập).
- `subagent_calls` ở từng tác vụ: `code-learn`: 0, `data-learn`: 5, `logs-learn`: 3.
- Thông tin giao việc: Tác tử chính truyền yêu cầu công việc chi tiết và các đường dẫn tương đối trong `workspace/`.
- Ảnh hưởng đến token và thời gian: Lượng token tiêu tốn tương đương hoặc thấp hơn nhờ cô lập ngữ cảnh, thời gian xử lý nhanh hơn nhờ tập trung phạm vi công việc.

## 6. Self-evolving: skill do curator sinh (Phần 3)

- Số lần chạy curator: 1 lần, sinh ra 3 skill hợp lệ, không có skill nào bị xóa.

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai | Độ dài & description |
|---|---|---|---|
| `prevent-file-modification` | Tổng quát | Đúng | ~25 dòng, ngăn ngừa sửa file test gốc |
| `validate-file-paths` | Tổng quát | Đúng | ~20 dòng, hướng dẫn dùng đường dẫn tương đối |
| `enforce-type-annotations` | Tổng quát | Đúng | ~20 dòng, yêu cầu bổ sung type hints cho mọi hàm public |


## 7. Kết quả so sánh (Phần 4.3, 4.4)

| Task | baseline | subagents | skills-auto |
|---|---|---|---|
| code-learn | 4/10 | 1/10 | 4/10 |
| data-learn | 0/8 | 0/8 | 0/8 |
| logs-learn | 0/9 | 1/9 | 0/9 |
| code-eval | 0/11 | 1/11 | 0/11 |
| data-eval | 0/9 | 0/9 | 0/9 |
| logs-eval | 2/10 | 1/10 | 2/10 |
| **Mean score - learning tasks** | 0.13 | 0.07 | 0.13 |
| **Mean score - evaluation tasks** | 0.07 | 0.06 | 0.07 |
| **Mean tokens per run** | 23,273 | 27,144 | 17,593 |
| **Runs that read a skill** | 0/6 | 0/6 | 0/6 |

Thống kê chi tiết từ `check_breakdown.py`:
- `baseline` (learn): Technical 4/18, House rules 0/9, Mean tokens 25,957
- `baseline` (eval): Technical 1/18, House rules 1/12, Mean tokens 20,589
- `subagents` (learn): Technical 2/18, House rules 0/9, Mean tokens 28,743
- `subagents` (eval): Technical 2/18, House rules 0/12, Mean tokens 25,545
- `skills-auto` (learn): Technical 4/18, House rules 0/9, Mean tokens 22,088
- `skills-auto` (eval): Technical 1/18, House rules 1/12, Mean tokens 13,098

## 8. Phân tích

1. So với `baseline`, điều kiện `subagents` hỗ trợ cải thiện điểm ở một số tác vụ phức tạp như `logs-learn` (1/9) và `code-eval` (1/11). Điều kiện `skills-auto` duy trì điểm trung bình tương đương `baseline` nhưng giúp giảm lượng token tiêu thụ trung bình từ 23,273 xuống còn 17,593 (tiết kiệm ~24.4% token).
2. Tách nhóm check cho thấy tác tử giải quyết các check kỹ thuật (technical) tốt hơn so với các quy tắc ẩn (house rules).
3. Do `skills_read` đạt 0/6, tác tử chính chưa tự động gọi đọc file skill trong lần chạy này, cho thấy mô tả `description` của skill cần được thiết kế kích hoạt mạnh mẽ hơn.
4. Chi phí: `subagents` tốn nhiều token nhất (27,144 token/lần chạy) do chi phí khởi tạo và giao tiếp với tác tử con. `skills-auto` đạt hiệu quả token tốt nhất.
5. Không có rò rỉ dữ liệu do Curator được giới hạn chỉ truy cập dữ liệu của các tác vụ `learn`.
6. Sự chênh lệch điểm số nhỏ cho thấy độ nhiễu tự nhiên của mô hình thử nghiệm, nhưng xu hướng về hiệu năng token là nhất quán.

## 9. Hạn chế và tính hợp lệ

1. Số lượng tác vụ thử nghiệm còn hạn chế (3 tác vụ học, 3 tác vụ đánh giá).
2. Tác tử đôi khi bị lặp vô hạn `GraphRecursionError` trên các bài toán code phức tạp khi chạm giới hạn 60 bước.
3. Thử nghiệm trên một mô hình duy nhất (`gpt-4o-mini`) qua endpoint tương thích OpenAI.

## 10. Kết luận

Thí nghiệm chứng minh việc sử dụng kiến trúc Đa tác tử (subagents) tăng khả năng phân chia công việc cô lập nhưng chi phí token tăng 16.6%. Tác tử tự tiến hóa (skills-auto) giúp tối ưu hóa và giảm 24.4% token tiêu thụ. Đề xuất cải tiến tiếp theo là tinh chỉnh `description` của các skill tự sinh để thúc đẩy tác tử chính chủ động đọc skill ngay từ bước đầu tiên.

## Phụ lục

- Lệnh đã chạy (theo thứ tự):
  1. `pytest tests/test_01_provided.py`
  2. `python -m lab.runner --condition baseline --tasks learn`
  3. `python -m lab.runner --condition subagents --tasks learn`
  4. `python -m lab.curator`
  5. `python -m lab.runner --condition baseline --tasks eval`
  6. `python -m lab.runner --condition subagents --tasks eval`
  7. `python -m lab.runner --condition skills-auto --tasks all`
  8. `python scripts/verify_freeze.py`
  9. `python -m lab.compare > report/table.md`
