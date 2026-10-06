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

> Dán nội dung `report/table.md` và kết quả `python scripts/check_breakdown.py`. Nêu các lần chạy có `error` hoặc `skills_modified = true` (nếu có) và cách xử lý.

```text
(dán bảng ở đây)
```

## 8. Phân tích

> Trả lời từng câu bằng số liệu từ mục 7 và bằng chứng từ vết. Kết quả âm hoặc không có khác biệt vẫn hợp lệ nếu được phân tích tốt.

1. So với `baseline`, điều kiện nào cải thiện điểm tác vụ **học**? Điều kiện nào cải thiện điểm tác vụ **đánh giá**? Có điều kiện nào cải thiện tác vụ học nhưng không cải thiện tác vụ đánh giá? Nếu có, đó là dấu hiệu gì?
2. Tách điểm thành check kỹ thuật và check quy ước (`rule_`). Skill do curator sinh giúp nhóm check nào? Check quy ước **mới** của tác vụ đánh giá có được skill giúp không, và vì sao?
3. Dựa vào vết và `skills_read`, giải thích một check mà skill giúp đạt và một check mà skill không giúp (skill chưa được đọc, đọc nhưng không làm theo, skill thiếu hoặc sai).
4. Chi phí: so sánh số token trung bình giữa các điều kiện. Điều kiện nào có hiệu quả tốt nhất theo điểm trên mỗi token? Đa tác tử có đáng chi phí trong thí nghiệm này không?
5. Có dấu hiệu rò rỉ dữ liệu hoặc quá khớp nào trong skill sinh ra không? Nhóm đã phòng tránh như thế nào?
6. Nhiễu: so sánh điểm tác vụ học của cùng bộ skill ở Phần 3.4 (đã sao lưu) và sau đóng băng. Chênh lệch bao nhiêu? Nó cho biết điều gì về độ tin cậy của các chênh lệch trong bảng ở mục 7?

## 9. Hạn chế và tính hợp lệ

> Nêu ít nhất 3 hạn chế và ảnh hưởng của từng hạn chế đến kết luận (ví dụ: chỉ 3 tác vụ mỗi vai trò, mỗi cấu hình chạy một lần, nhiễu của mô hình, tác vụ do giảng viên thiết kế sẵn quy ước, chỉ một mô hình).

1.
2.
3.

## 10. Kết luận

> Tối đa 5 câu. Chỉ khẳng định điều số liệu hỗ trợ. Nêu một đề xuất cải tiến tiếp theo.

## Phụ lục

- Lệnh đã chạy (theo thứ tự):
- Thử thách mở rộng (nếu có): hướng chọn, kết quả, nhận xét.
- Ghi chú khác:
