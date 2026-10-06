"""GUIDE Phần 1 - Định nghĩa subagent (tác tử con).   >>> SINH VIÊN CÀI ĐẶT <<<

Pseudo-code: guides/pseudocode/02_subagents.md
Kiểm tra:    pytest tests/test_02_agent.py
"""


def get_subagents() -> list[dict]:
    """Trả về danh sách subagent (ít nhất 2, tên khác nhau).

    Mỗi phần tử là một dict có các khóa bắt buộc:
      "name":          tên duy nhất (chữ thường, có thể có dấu gạch ngang)
      "description":   khi nào tác tử chính nên giao việc cho subagent này (viết như một hướng dẫn hành động)
      "system_prompt": chỉ dẫn cho subagent
    Gợi ý vai trò: explorer (đọc và báo cáo), implementer (thực hiện), reviewer (kiểm tra độc lập).
    """
    return [
        {
            "name": "explorer",
            "description": "Dùng khi cần đọc, khám phá tài liệu, kiểm tra cấu trúc file và dữ liệu mẫu mà không sửa đổi gì. Trả về báo cáo tổng quan ngắn gọn.",
            "system_prompt": "Bạn là explorer. Nhiệm vụ của bạn là đọc các tệp tin, xem cấu trúc dữ liệu, kiểm tra mã nguồn hoặc log và đưa ra báo cáo ngắn gọn, chính xác cho tác tử chính. Tuyệt đối không chỉnh sửa tệp hay thay đổi hệ thống.",
        },
        {
            "name": "implementer",
            "description": "Dùng khi cần thực hiện thay đổi mã nguồn, chỉnh sửa dữ liệu, viết lại script hoặc chạy bài test và báo cáo kết quả cụ thể.",
            "system_prompt": "Bạn là implementer. Nhiệm vụ của bạn là thực thi các thay đổi mã nguồn, sửa lỗi, viết các hàm cần thiết, chạy thử nghiệm/kiểm thử và báo cáo kết quả thực hiện cho tác tử chính.",
        },
        {
            "name": "reviewer",
            "description": "Dùng khi cần kiểm tra độc lập kết quả làm việc so với yêu cầu đề bài, rà soát các trường hợp biên (edge cases) và kiểm thử quy tắc.",
            "system_prompt": "Bạn là reviewer. Nhiệm vụ của bạn là đánh giá độc lập kết quả đầu ra, kiểm tra các trường hợp đặc biệt và quy tắc đề bài đề ra mà không thực hiện chỉnh sửa.",
        },
    ]
