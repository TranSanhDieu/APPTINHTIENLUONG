
import streamlit as st
import pandas as pd
from io import BytesIO
# =====================================================
# 1. CẤU HÌNH ỨNG DỤNG
# =====================================================

st.set_page_config(
    page_title="Tính lương và thuế TNCN",
    page_icon="💰",
    layout="wide"
)

st.title("💰 ỨNG DỤNG TÍNH LƯƠNG VÀ THUẾ TNCN TỐI ĐA 500 NGƯỜI LAO ĐỘNG - NGUYỄN CHÍ THANH")
st.caption("Tính lương hàng loạt cho tối đa 500 người lao động")

st.info(
    "Đơn vị tiền: triệu đồng/tháng. "
    "Công thức thuế và các mức giảm trừ đang theo mô hình ban đầu của bạn, "
    "không mặc nhiên là quy định pháp luật hiện hành."
)

# =====================================================
# 2. HÀM TÍNH TOÁN
# =====================================================

def tinh_thue_tncn(thu_nhap_tinh_thue):
    """Tính thuế TNCN theo biểu thuế 5 bậc của code gốc."""

    if thu_nhap_tinh_thue <= 0:
        return 0.0

    if thu_nhap_tinh_thue <= 10:
        return thu_nhap_tinh_thue * 0.05

    elif thu_nhap_tinh_thue <= 30:
        return thu_nhap_tinh_thue * 0.10 - 0.5

    elif thu_nhap_tinh_thue <= 60:
        return thu_nhap_tinh_thue * 0.20 - 3.5

    elif thu_nhap_tinh_thue <= 100:
        return thu_nhap_tinh_thue * 0.30 - 9.5

    else:
        return thu_nhap_tinh_thue * 0.35 - 14.5


def dinh_dang_tien(x):
    """Định dạng số theo cách viết số Việt Nam."""
    return f"{x:,.3f}".replace(",", "X").replace(".", ",").replace("X", ".")


def tao_du_lieu_ban_dau(so_luong):
    """Tạo bảng nhập liệu cho số nhân viên đã chọn."""

    return pd.DataFrame({
        "Mã nhân viên": [
            f"NV{i:03d}" for i in range(1, so_luong + 1)
        ],
        "Họ và tên": ["" for _ in range(so_luong)],
        "Lương cơ bản": [15.0 for _ in range(so_luong)],
        "Tiền thưởng": [0.0 for _ in range(so_luong)],
        "Phụ cấp tính BHXH": [0.0 for _ in range(so_luong)],
        "Phụ cấp không tính BHXH": [0.0 for _ in range(so_luong)],
        "Số người phụ thuộc": [0 for _ in range(so_luong)]
    })


# =====================================================
# 3. CHỌN SỐ LƯỢNG NGƯỜI LAO ĐỘNG
# =====================================================

st.subheader("1. Chọn số lượng người lao động")

so_luong = st.number_input(
    "Bạn cần tính lương cho bao nhiêu người?",
    min_value=1,
    max_value=500,
    value=10,
    step=1,
    key="so_luong_nhan_vien"
)

st.caption(
    f"Đang chọn {so_luong} người lao động. "
    "Bạn có thể nhập hoặc dán dữ liệu trực tiếp vào bảng bên dưới."
)

# Dùng key riêng cho mỗi số lượng để bảng có đúng số dòng.
editor_key = f"bang_nhap_luong_{so_luong}"

if editor_key not in st.session_state:
    st.session_state[editor_key] = tao_du_lieu_ban_dau(so_luong)

# =====================================================
# 4. NHẬP DỮ LIỆU NHÂN VIÊN
# =====================================================

st.subheader("2. Nhập thông tin tiền lương")

st.write(
    "Các cột tiền lương nhập bằng triệu đồng. "
    "Cột số người phụ thuộc chỉ nhận số nguyên không âm."
)

du_lieu_nhap = st.data_editor(
    st.session_state[editor_key],
    key=f"editor_{so_luong}",
    num_rows="fixed",
    use_container_width=True,
    hide_index=True,
    height=min(620, 38 * (int(so_luong) + 1)),
    column_config={
        "Mã nhân viên": st.column_config.TextColumn(
            "Mã nhân viên",
            required=True
        ),
        "Họ và tên": st.column_config.TextColumn(
            "Họ và tên"
        ),
        "Lương cơ bản": st.column_config.NumberColumn(
            "Lương cơ bản (triệu)",
            min_value=0.0,
            max_value=1000000.0,
            step=0.5,
            format="%.3f"
        ),
        "Tiền thưởng": st.column_config.NumberColumn(
            "Tiền thưởng (triệu)",
            min_value=0.0,
            max_value=1000000.0,
            step=0.5,
            format="%.3f"
        ),
        "Phụ cấp tính BHXH": st.column_config.NumberColumn(
            "Phụ cấp tính BHXH (triệu)",
            min_value=0.0,
            max_value=1000000.0,
            step=0.5,
            format="%.3f"
        ),
        "Phụ cấp không tính BHXH": st.column_config.NumberColumn(
            "Phụ cấp không tính BHXH (triệu)",
            min_value=0.0,
            max_value=1000000.0,
            step=0.5,
            format="%.3f"
        ),
        "Số người phụ thuộc": st.column_config.NumberColumn(
            "Người phụ thuộc",
            min_value=0,
            max_value=100,
            step=1,
            format="%d"
        )
    }
)

# =====================================================
# 5. NÚT TÍNH TOÁN
# =====================================================

if st.button(
    "🧮 TÍNH LƯƠNG CHO TOÀN BỘ NHÂN VIÊN",
    type="primary",
    use_container_width=True
):

    bang = du_lieu_nhap.copy()

    # Chuẩn hóa và kiểm tra dữ liệu
    cac_cot_tien = [
        "Lương cơ bản",
        "Tiền thưởng",
        "Phụ cấp tính BHXH",
        "Phụ cấp không tính BHXH"
    ]

    for cot in cac_cot_tien:
        bang[cot] = pd.to_numeric(
            bang[cot], errors="coerce"
        )

    bang["Số người phụ thuộc"] = pd.to_numeric(
        bang["Số người phụ thuộc"], errors="coerce"
    )

    loi = []

    if bang["Mã nhân viên"].isna().any():
        loi.append("Có nhân viên chưa nhập mã nhân viên.")

    bang["Mã nhân viên"] = (
        bang["Mã nhân viên"].fillna("").astype(str).str.strip()
    )

    if (bang["Mã nhân viên"] == "").any():
        loi.append("Mã nhân viên không được để trống.")

    if bang["Mã nhân viên"].duplicated().any():
        loi.append("Mã nhân viên bị trùng. Vui lòng kiểm tra lại.")

    if bang[cac_cot_tien].isna().any().any():
        loi.append("Có ô tiền lương trống hoặc không phải số.")

    if (bang[cac_cot_tien] < 0).any().any():
        loi.append("Tiền lương, thưởng và phụ cấp không được âm.")

    if bang["Số người phụ thuộc"].isna().any():
        loi.append("Số người phụ thuộc không được để trống.")

    if (
        (bang["Số người phụ thuộc"] < 0)
        | (bang["Số người phụ thuộc"] % 1 != 0)
    ).any():
        loi.append("Số người phụ thuộc phải là số nguyên không âm.")

    if loi:
        for thong_bao in loi:
            st.error(thong_bao)

    else:
        bang["Số người phụ thuộc"] = (
            bang["Số người phụ thuộc"].astype(int)
        )

        # Tổng thu nhập
        bang["Tổng thu nhập"] = (
            bang["Lương cơ bản"]
            + bang["Tiền thưởng"]
            + bang["Phụ cấp tính BHXH"]
            + bang["Phụ cấp không tính BHXH"]
        )

        # Bảo hiểm theo mô hình ban đầu
        bang["Tiền đóng BHXH"] = (
            bang["Lương cơ bản"]
            + bang["Phụ cấp tính BHXH"]
        ) * 0.105

        # Thu nhập tính thuế theo giả định ban đầu
        bang["Thu nhập tính thuế"] = (
            bang["Tổng thu nhập"]
            - 15.5
            - 6.2 * bang["Số người phụ thuộc"]
            - bang["Tiền đóng BHXH"]
        )

        # Thuế TNCN
        bang["Thuế TNCN"] = bang["Thu nhập tính thuế"].apply(
            tinh_thue_tncn
        )

        # Thực lãnh
        bang["Thực lãnh"] = (
            bang["Tổng thu nhập"]
            - bang["Tiền đóng BHXH"]
            - bang["Thuế TNCN"]
        )

        # Lưu kết quả vào session để có thể tải Excel
        st.session_state["ket_qua_bang_luong"] = bang.copy()
        st.session_state["so_luong_da_tinh"] = int(so_luong)

        st.success(
            f"Đã tính toán thành công cho {len(bang)} người lao động."
        )


# =====================================================
# 6. HIỂN THỊ BẢNG KẾT QUẢ VÀ TỔNG HỢP
# =====================================================

if "ket_qua_bang_luong" in st.session_state:

    bang_kq = st.session_state["ket_qua_bang_luong"]

    st.divider()
    st.subheader("3. Bảng lương chi tiết")

    cac_cot_ket_qua = [
        "Mã nhân viên",
        "Họ và tên",
        "Lương cơ bản",
        "Tiền thưởng",
        "Phụ cấp tính BHXH",
        "Phụ cấp không tính BHXH",
        "Số người phụ thuộc",
        "Tổng thu nhập",
        "Tiền đóng BHXH",
        "Thu nhập tính thuế",
        "Thuế TNCN",
        "Thực lãnh"
    ]

    st.dataframe(
        bang_kq[cac_cot_ket_qua].style.format({
            cot: "{:,.3f}"
            for cot in [
                "Lương cơ bản",
                "Tiền thưởng",
                "Phụ cấp tính BHXH",
                "Phụ cấp không tính BHXH",
                "Tổng thu nhập",
                "Tiền đóng BHXH",
                "Thu nhập tính thuế",
                "Thuế TNCN",
                "Thực lãnh"
            ]
        }),
        use_container_width=True,
        hide_index=True,
        height=450
    )

    # Tổng hợp toàn bộ nhân viên
    tong_thu_nhap = bang_kq["Tổng thu nhập"].sum()
    tong_bhxh = bang_kq["Tiền đóng BHXH"].sum()
    tong_thue = bang_kq["Thuế TNCN"].sum()
    tong_thuc_lanh = bang_kq["Thực lãnh"].sum()

    st.subheader("4. Tổng hợp quỹ lương")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Số nhân viên",
        f"{len(bang_kq):,}"
    )

    c2.metric(
        "Tổng thu nhập",
        f"{dinh_dang_tien(tong_thu_nhap)} triệu"
    )

    c3.metric(
        "Tổng thuế TNCN",
        f"{dinh_dang_tien(tong_thue)} triệu"
    )

    c4.metric(
        "Tổng thực lãnh",
        f"{dinh_dang_tien(tong_thuc_lanh)} triệu"
    )

    st.write(
        f"**Tổng tiền đóng BHXH:** "
        f"{dinh_dang_tien(tong_bhxh)} triệu đồng"
    )

    # =================================================
    # 7. XUẤT EXCEL GỒM 2 SHEET
    # =================================================

    def tao_file_excel(dataframe):
        """Tạo file Excel có bảng chi tiết và bảng tổng hợp."""

        output = BytesIO()

        cot_chi_tiet = [
            "Mã nhân viên",
            "Họ và tên",
            "Lương cơ bản",
            "Tiền thưởng",
            "Phụ cấp tính BHXH",
            "Phụ cấp không tính BHXH",
            "Số người phụ thuộc",
            "Tổng thu nhập",
            "Tiền đóng BHXH",
            "Thu nhập tính thuế",
            "Thuế TNCN",
            "Thực lãnh"
        ]

        bang_chi_tiet = dataframe[cot_chi_tiet].copy()

        bang_tong_hop = pd.DataFrame({
            "Chỉ tiêu": [
                "Số người lao động",
                "Tổng thu nhập",
                "Tổng tiền đóng BHXH",
                "Tổng thu nhập tính thuế",
                "Tổng thuế TNCN",
                "Tổng tiền thực lãnh"
            ],
            "Giá trị": [
                len(dataframe),
                dataframe["Tổng thu nhập"].sum(),
                dataframe["Tiền đóng BHXH"].sum(),
                dataframe["Thu nhập tính thuế"].sum(),
                dataframe["Thuế TNCN"].sum(),
                dataframe["Thực lãnh"].sum()
            ],
            "Đơn vị": [
                "Người",
                "Triệu đồng",
                "Triệu đồng",
                "Triệu đồng",
                "Triệu đồng",
                "Triệu đồng"
            ]
        })

        with pd.ExcelWriter(
            output,
            engine="openpyxl"
        ) as writer:

            bang_chi_tiet.to_excel(
                writer,
                sheet_name="Bang luong chi tiet",
                index=False
            )

            bang_tong_hop.to_excel(
                writer,
                sheet_name="Tong hop quy luong",
                index=False
            )

            # Định dạng độ rộng cột và cố định hàng tiêu đề
            for sheet_name in [
                "Bang luong chi tiet",
                "Tong hop quy luong"
            ]:
                ws = writer.sheets[sheet_name]
                ws.freeze_panes = "A2"
                ws.auto_filter.ref = ws.dimensions

                for column_cells in ws.columns:
                    max_length = max(
                        len(str(cell.value or ""))
                        for cell in column_cells
                    )
                    ws.column_dimensions[
                        column_cells[0].column_letter
                    ].width = min(max_length + 3, 35)

            # Định dạng các cột tiền trên sheet chi tiết
            ws = writer.sheets["Bang luong chi tiet"]

            cot_tien_excel = [
                "Lương cơ bản",
                "Tiền thưởng",
                "Phụ cấp tính BHXH",
                "Phụ cấp không tính BHXH",
                "Tổng thu nhập",
                "Tiền đóng BHXH",
                "Thu nhập tính thuế",
                "Thuế TNCN",
                "Thực lãnh"
            ]

            for ten_cot in cot_tien_excel:
                so_cot = cot_chi_tiet.index(ten_cot) + 1

                for hang in range(2, ws.max_row + 1):
                    ws.cell(
                        row=hang,
                        column=so_cot
                    ).number_format = '#,##0.000'

            ws2 = writer.sheets["Tong hop quy luong"]

            for hang in range(3, ws2.max_row + 1):
                ws2.cell(
                    row=hang,
                    column=2
                ).number_format = '#,##0.000'

        output.seek(0)
        return output.getvalue()

    file_excel = tao_file_excel(bang_kq)

    st.divider()
    st.subheader("5. Xuất dữ liệu ra Excel")

    st.download_button(
        label="📥 TẢI FILE EXCEL BẢNG LƯƠNG",
        data=file_excel,
        file_name="Bang_luong_va_thue_TNCN.xlsx",
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        type="primary",
        use_container_width=True
    )

    st.caption(
        "File Excel gồm 2 trang tính: bảng lương chi tiết từng nhân viên "
        "và bảng tổng hợp quỹ lương. Đơn vị các khoản tiền là triệu đồng."
    )

    if st.button("🗑️ XÓA KẾT QUẢ ĐÃ TÍNH"):
        del st.session_state["ket_qua_bang_luong"]
        if "so_luong_da_tinh" in st.session_state:
            del st.session_state["so_luong_da_tinh"]
        st.rerun()
