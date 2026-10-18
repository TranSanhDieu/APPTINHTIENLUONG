import streamlit as st

# ==========================================
# CẤU HÌNH TRANG WEB
# ==========================================
st.set_page_config(
    page_title="Tính thuế TNCN và lương thực lãnh",
    page_icon="💰",
    layout="centered"
)

# ==========================================
# TIÊU ĐỀ
# ==========================================
st.title("💰 TÍNH THUẾ TNCN VÀ LƯƠNG THỰC LÃNH")
st.caption(
    "Công cụ ước tính thuế thu nhập cá nhân và tiền lương "
    "thực nhận hằng tháng của người lao động."
)

st.info(
    "Nhập các khoản thu nhập theo đơn vị triệu đồng/tháng. "
    "Kết quả được tính tự động dựa trên các thông tin đã nhập."
)

# ==========================================
# NHẬP THÔNG TIN
# ==========================================
st.subheader("1. Thông tin tiền lương")

col1, col2 = st.columns(2)

with col1:
    luong_co_ban = st.number_input(
        "Lương cơ bản (triệu đồng)",
        min_value=0.0,
        value=10.0,
        step=0.5,
        format="%.2f"
    )

    thuong = st.number_input(
        "Tiền thưởng (triệu đồng)",
        min_value=0.0,
        value=0.0,
        step=0.5,
        format="%.2f"
    )

with col2:
    phu_cap_co_bhxh = st.number_input(
        "Phụ cấp tính đóng BHXH (triệu đồng)",
        min_value=0.0,
        value=0.0,
        step=0.5,
        format="%.2f"
    )

    phu_cap_khong_bhxh = st.number_input(
        "Phụ cấp không tính đóng BHXH (triệu đồng)",
        min_value=0.0,
        value=0.0,
        step=0.5,
        format="%.2f"
    )

so_nguoi_phu_thuoc = st.number_input(
    "Số người phụ thuộc",
    min_value=0,
    value=0,
    step=1
)

# ==========================================
# CÁC MỨC GIẢM TRỪ VÀ TỶ LỆ
# ==========================================
st.subheader("2. Tham số tính thuế")

with st.expander("Xem và điều chỉnh tham số tính thuế"):
    giam_tru_ban_than = st.number_input(
        "Giảm trừ bản thân (triệu đồng/tháng)",
        min_value=0.0,
        value=15.5,
        step=0.5,
        format="%.2f"
    )

    giam_tru_phu_thuoc = st.number_input(
        "Giảm trừ mỗi người phụ thuộc (triệu đồng/tháng)",
        min_value=0.0,
        value=6.2,
        step=0.1,
        format="%.2f"
    )

    ty_le_bao_hiem = st.number_input(
        "Tỷ lệ bảo hiểm người lao động đóng (%)",
        min_value=0.0,
        max_value=100.0,
        value=10.5,
        step=0.5,
        format="%.2f"
    )

st.caption(
    "Mặc định theo bài toán: giảm trừ bản thân 15,5 triệu đồng, "
    "người phụ thuộc 6,2 triệu đồng và tỷ lệ bảo hiểm 10,5%. "
    "Cần kiểm tra căn cứ đóng bảo hiểm và các khoản giảm trừ "
    "thực tế trước khi sử dụng."
)

# ==========================================
# HÀM ĐỊNH DẠNG TIỀN
# ==========================================
def dinh_dang_tien(gia_tri):
    return f"{gia_tri:,.2f} triệu đồng".replace(",", "X").replace(".", ",").replace("X", ".")


# ==========================================
# TÍNH TOÁN
# ==========================================
tong_thu_nhap = (
    luong_co_ban
    + thuong
    + phu_cap_co_bhxh
    + phu_cap_khong_bhxh
)

# Mô phỏng theo công thức ban đầu:
# BHXH, BHYT, BHTN = 10,5% x (lương cơ bản + phụ cấp đóng BHXH)
luong_lam_can_cu_bao_hiem = luong_co_ban + phu_cap_co_bhxh
tien_dong_bao_hiem = luong_lam_can_cu_bao_hiem * ty_le_bao_hiem / 100

tong_giam_tru_gia_canh = (
    giam_tru_ban_than
    + giam_tru_phu_thuoc * so_nguoi_phu_thuoc
)

thu_nhap_tinh_thue = max(
    0.0,
    tong_thu_nhap
    - tien_dong_bao_hiem
    - tong_giam_tru_gia_canh
)

# Biểu thuế lũy tiến từng phần 5 bậc
# Công thức rút gọn theo các mức thu nhập tính thuế hằng tháng
if thu_nhap_tinh_thue <= 10:
    thue_tncn = thu_nhap_tinh_thue * 0.05
elif thu_nhap_tinh_thue <= 30:
    thue_tncn = thu_nhap_tinh_thue * 0.10 - 0.5
elif thu_nhap_tinh_thue <= 60:
    thue_tncn = thu_nhap_tinh_thue * 0.20 - 3.5
elif thu_nhap_tinh_thue <= 100:
    thue_tncn = thu_nhap_tinh_thue * 0.30 - 9.5
else:
    thue_tncn = thu_nhap_tinh_thue * 0.35 - 14.5

# Đảm bảo thuế không âm
thue_tncn = max(0.0, thue_tncn)

# Tiền thực lãnh
thuc_lanh = tong_thu_nhap - tien_dong_bao_hiem - thue_tncn

# ==========================================
# HIỂN THỊ KẾT QUẢ
# ==========================================
st.divider()
st.subheader("3. Kết quả tính toán")

col1, col2 = st.columns(2)

with col1:
    st.metric(
        label="Tổng thu nhập",
        value=dinh_dang_tien(tong_thu_nhap)
    )

    st.metric(
        label="Tổng tiền bảo hiểm",
        value=dinh_dang_tien(tien_dong_bao_hiem)
    )

with col2:
    st.metric(
        label="Thuế TNCN phải nộp",
        value=dinh_dang_tien(thue_tncn)
    )

    st.metric(
        label="Thu nhập tính thuế",
        value=dinh_dang_tien(thu_nhap_tinh_thue)
    )

st.success(f"💵 TIỀN THỰC LÃNH: {dinh_dang_tien(thuc_lanh)}")

# ==========================================
# BẢNG CHI TIẾT
# ==========================================
st.subheader("4. Bảng chi tiết thu nhập và khấu trừ")

chi_tiet = {
    "Nội dung": [
        "Lương cơ bản",
        "Tiền thưởng",
        "Phụ cấp tính đóng BHXH",
        "Phụ cấp không tính đóng BHXH",
        "Tổng thu nhập",
        "Tiền đóng bảo hiểm",
        "Giảm trừ bản thân",
        "Giảm trừ người phụ thuộc",
        "Thu nhập tính thuế",
        "Thuế thu nhập cá nhân",
        "TIỀN THỰC LÃNH"
    ],
    "Số tiền (triệu đồng)": [
        luong_co_ban,
        thuong,
        phu_cap_co_bhxh,
        phu_cap_khong_bhxh,
        tong_thu_nhap,
        tien_dong_bao_hiem,
        giam_tru_ban_than,
        giam_tru_phu_thuoc * so_nguoi_phu_thuoc,
        thu_nhap_tinh_thue,
        thue_tncn,
        thuc_lanh
    ]
}

st.dataframe(
    [
        {
            "Nội dung": dong["Nội dung"],
            "Số tiền (triệu đồng)": round(
                dong["Số tiền (triệu đồng)"], 2
            )
        }
        for dong in [
            {"Nội dung": ten, "Số tiền (triệu đồng)": tien}
            for ten, tien in zip(
                chi_tiet["Nội dung"],
                chi_tiet["Số tiền (triệu đồng)"]
            )
        ]
    ],
    use_container_width=True,
    hide_index=True
)

# ==========================================
# GIẢI THÍCH CÔNG THỨC
# ==========================================
with st.expander("📘 Xem công thức tính"):
    st.markdown(
        """
        **1. Tổng thu nhập**

        Tổng thu nhập = Lương cơ bản + Tiền thưởng
        + Phụ cấp tính đóng BHXH + Phụ cấp không tính đóng BHXH.

        **2. Tiền đóng bảo hiểm (mô phỏng)**

        Tiền bảo hiểm = (Lương cơ bản + Phụ cấp tính đóng BHXH)
        × Tỷ lệ bảo hiểm người lao động đóng.

        **3. Thu nhập tính thuế**

        Thu nhập tính thuế = Tổng thu nhập − Tiền bảo hiểm
        − Giảm trừ bản thân − Giảm trừ người phụ thuộc.

        Nếu kết quả âm thì thu nhập tính thuế được tính bằng 0.

        **4. Tiền thực lãnh**

        Tiền thực lãnh = Tổng thu nhập − Tiền bảo hiểm − Thuế TNCN.
        """
    )

st.caption(
    "Lưu ý: Đây là công cụ ước tính theo mô hình đã thiết lập, "
    "không thay thế việc xác định thu nhập chịu thuế, căn cứ đóng "
    "bảo hiểm và các khoản miễn, giảm trừ theo hồ sơ thực tế."
  )
