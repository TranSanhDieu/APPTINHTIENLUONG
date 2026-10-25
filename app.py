import streamlit as st
import pandas as pd
import math

# ==========================================
# 1. CẤU HÌNH TRANG
# ==========================================
st.set_page_config(
    page_title="Phân tích hiệu quả dự án đầu tư",
    page_icon="📊",
    layout="wide"
)

# ==========================================
# 2. TIÊU ĐỀ VÀ GIAO DIỆN
# ==========================================
st.title("📊 PHÂN TÍCH HIỆU QUẢ DỰ ÁN ĐẦU TƯ")
st.caption(
    "Công cụ tính NPV, IRR, MIRR, PI, PP và DPP "
    "phục vụ phân tích tài chính dự án."
)

st.info(
    "Nhập dòng tiền theo từng năm. Dùng cùng một đơn vị tiền tệ "
    "cho toàn bộ dự án, ví dụ: triệu đồng hoặc tỷ đồng."
)

# ==========================================
# 3. HÀM ĐỊNH DẠNG
# ==========================================
def format_money(value):
    if value is None or not math.isfinite(value):
        return "Không xác định"
    return f"{value:,.2f}"


def format_year(value):
    if value is None or not math.isfinite(value):
        return "Không hoàn vốn"
    return f"{value:.2f} năm"


def safe_divide(a, b):
    if abs(b) < 1e-12:
        return None
    return a / b


# ==========================================
# 4. HÀM TÍNH TOÁN TÀI CHÍNH
# ==========================================
def calculate_npv(rate, cash_flows):
    """NPV: dòng tiền đầu tiên tại thời điểm năm 0."""
    return sum(
        cf / (1 + rate) ** t
        for t, cf in enumerate(cash_flows)
    )


def calculate_irr(cash_flows):
    """
    Tìm IRR bằng phương pháp chia đôi.
    Chỉ trả về nghiệm tìm được trong khoảng khảo sát.
    Có thể không tìm được nếu dòng tiền không có IRR thực
    trong khoảng hoặc có nhiều nghiệm.
    """
    if not any(cf > 0 for cf in cash_flows):
        return None

    if not any(cf < 0 for cf in cash_flows):
        return None

    def npv_at_rate(rate):
        if rate <= -1:
            return float("nan")
        try:
            return sum(
                cf / (1 + rate) ** t
                for t, cf in enumerate(cash_flows)
            )
        except (OverflowError, ZeroDivisionError):
            return float("nan")

    # Quét khoảng lãi suất để tìm đoạn có đổi dấu
    grid = [-0.9999]
    grid.extend(
        [-0.99, -0.95, -0.9, -0.8, -0.6, -0.4, -0.2, 0.0]
    )
    grid.extend(
        [0.01, 0.05, 0.1, 0.2, 0.3, 0.5, 0.75, 1.0,
         1.5, 2.0, 3.0, 5.0, 10.0, 20.0, 50.0, 100.0]
    )

    previous_rate = grid[0]
    previous_value = npv_at_rate(previous_rate)

    # Ưu tiên nghiệm có NPV bằng 0 tại một điểm trong lưới
    for rate in grid:
        value = npv_at_rate(rate)

        if math.isfinite(value) and abs(value) < 1e-10:
            return rate

        if (
            math.isfinite(previous_value)
            and math.isfinite(value)
            and previous_value * value < 0
        ):
            low = previous_rate
            high = rate
            f_low = previous_value

            for _ in range(300):
                mid = (low + high) / 2
                f_mid = npv_at_rate(mid)

                if not math.isfinite(f_mid):
                    break

                if abs(f_mid) < 1e-10:
                    return mid

                if f_low * f_mid <= 0:
                    high = mid
                else:
                    low = mid
                    f_low = f_mid

            return (low + high) / 2

        previous_rate = rate
        previous_value = value

    return None


def calculate_mirr(cash_flows, finance_rate, reinvest_rate):
    """
    MIRR = (FV dòng tiền dương / PV dòng tiền âm)
           ** (1 / số kỳ) - 1

    Tài trợ dòng tiền âm theo finance_rate;
    tái đầu tư dòng tiền dương theo reinvest_rate.
    """
    periods = len(cash_flows) - 1

    if periods <= 0:
        return None

    if not any(cf > 0 for cf in cash_flows):
        return None

    if not any(cf < 0 for cf in cash_flows):
        return None

    pv_negative = sum(
        abs(cf) / (1 + finance_rate) ** t
        for t, cf in enumerate(cash_flows)
        if cf < 0
    )

    fv_positive = sum(
        cf * (1 + reinvest_rate) ** (periods - t)
        for t, cf in enumerate(cash_flows)
        if cf > 0
    )

    if pv_negative <= 0 or fv_positive < 0:
        return None

    if fv_positive == 0:
        return -1.0

    return (fv_positive / pv_negative) ** (1 / periods) - 1


def calculate_payback(cash_flows, discount_rate=0.0):
    """
    PP: dùng dòng tiền chưa chiết khấu.
    DPP: dùng dòng tiền đã chiết khấu.

    Trả về số năm hoàn vốn có xét phần năm lẻ.
    """
    cumulative = cash_flows[0]

    if cumulative >= 0:
        return 0.0

    for t in range(1, len(cash_flows)):
        cf = cash_flows[t] / (1 + discount_rate) ** t
        previous = cumulative
        cumulative += cf

        if cumulative >= 0 and cf > 0:
            return (t - 1) + abs(previous) / cf

    return None


# ==========================================
# 5. NHẬP DỮ LIỆU DỰ ÁN
# ==========================================
st.subheader("1. Thông tin dự án")

col1, col2, col3 = st.columns(3)

with col1:
    don_vi_tien = st.selectbox(
        "Đơn vị tiền tệ",
        ["Triệu đồng", "Tỷ đồng", "Nghìn đồng", "Đồng"]
    )

with col2:
    so_nam = st.number_input(
        "Thời gian dự án (năm)",
        min_value=1,
        max_value=50,
        value=5,
        step=1
    )

with col3:
    von_dau_tu = st.number_input(
        "Vốn đầu tư ban đầu",
        min_value=0.01,
        value=1000.0,
        step=100.0,
        format="%.2f"
    )

st.caption(
    "Vốn đầu tư ban đầu được nhập dưới dạng số dương; "
    "ứng dụng tự động chuyển thành dòng tiền âm tại năm 0."
)

# ==========================================
# 6. NHẬP DÒNG TIỀN HẰNG NĂM
# ==========================================
st.subheader("2. Dòng tiền dự kiến của dự án")

st.write(
    "Nhập dòng tiền ròng của từng năm sau năm đầu tư. "
    "Dòng tiền có thể dương hoặc âm."
)

# Giá trị mẫu theo ví dụ ban đầu:
# Năm 0 = -1000; năm 1 = -200; năm 2 = -100;
# năm 3 = 300; năm 4 = 800; năm 5 = 1200.
gia_tri_mau = [-200.0, -100.0, 300.0, 800.0, 1200.0]

cash_flows = []

# Dùng form để tránh tính lại khi đang nhập từng năm
with st.form("cash_flow_form"):
    cols = st.columns(3)

    for i in range(int(so_nam)):
        with cols[i % 3]:
            default_value = (
                gia_tri_mau[i] if i < len(gia_tri_mau) else 0.0
            )

            cf = st.number_input(
                f"Dòng tiền năm {i + 1} ({don_vi_tien})",
                value=float(default_value),
                step=100.0,
                format="%.2f",
                key=f"cash_flow_{i}"
            )
            cash_flows.append(cf)

    submitted = st.form_submit_button(
        "🧮 TÍNH TOÁN HIỆU QUẢ DỰ ÁN",
        use_container_width=True
    )

# ==========================================
# 7. THÔNG SỐ CHIẾT KHẤU
# ==========================================
st.subheader("3. Các tỷ lệ tài chính")

col1, col2 = st.columns(2)

with col1:
    discount_rate_pct = st.number_input(
        "Tỷ lệ chiết khấu / chi phí sử dụng vốn (%)",
        min_value=0.0,
        max_value=1000.0,
        value=20.0,
        step=1.0
    )

with col2:
    reinvest_rate_pct = st.number_input(
        "Tỷ lệ tái đầu tư dùng cho MIRR (%)",
        min_value=0.0,
        max_value=1000.0,
        value=20.0,
        step=1.0
    )

st.caption(
    "MIRR sử dụng chi phí tài trợ bằng tỷ lệ chiết khấu "
    "và tỷ lệ tái đầu tư theo thông số riêng ở trên."
)

# ==========================================
# 8. TÍNH TOÁN VÀ HIỂN THỊ KẾT QUẢ
# ==========================================
if submitted:
    r = discount_rate_pct / 100
    finance_rate = r
    reinvest_rate = reinvest_rate_pct / 100

    # Dòng tiền đầy đủ, bao gồm năm 0
    full_cash_flows = [-float(von_dau_tu)] + cash_flows

    # NPV
    npv = calculate_npv(r, full_cash_flows)

    # IRR
    irr = calculate_irr(full_cash_flows)

    # MIRR
    mirr = calculate_mirr(
        full_cash_flows,
        finance_rate,
        reinvest_rate
    )

    # PI: PV dòng tiền thu vào / PV dòng tiền chi ra
    pv_benefits = sum(
        cf / (1 + r) ** t
        for t, cf in enumerate(full_cash_flows)
        if cf > 0
    )

    pv_costs = sum(
        abs(cf) / (1 + r) ** t
        for t, cf in enumerate(full_cash_flows)
        if cf < 0
    )

    pi = safe_divide(pv_benefits, pv_costs)

    # PP và DPP
    pp = calculate_payback(full_cash_flows, 0.0)
    dpp = calculate_payback(full_cash_flows, r)

    # ======================================
    # HIỂN THỊ CÁC CHỈ TIÊU
    # ======================================
    st.divider()
    st.subheader("4. Kết quả phân tích")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("NPV", f"{format_money(npv)} {don_vi_tien}")
        st.metric(
            "IRR",
            f"{irr * 100:.2f}%" if irr is not None else "Không xác định"
        )

    with col2:
        st.metric(
            "MIRR",
            f"{mirr * 100:.2f}%" if mirr is not None else "Không xác định"
        )
        st.metric(
            "PI",
            f"{pi:.4f}" if pi is not None else "Không xác định"
        )

    with col3:
        st.metric("PP", format_year(pp))
        st.metric("DPP", format_year(dpp))

    # ======================================
    # ĐÁNH GIÁ SƠ BỘ
    # ======================================
    st.subheader("5. Đánh giá sơ bộ dự án")

    if npv > 0:
        st.success(
            "NPV > 0: Dự án tạo ra giá trị hiện tại ròng dương "
            "theo tỷ lệ chiết khấu đã chọn."
        )
    elif npv < 0:
        st.warning(
            "NPV < 0: Dự án chưa đạt mức sinh lời yêu cầu "
            "theo tỷ lệ chiết khấu đã chọn."
        )
    else:
        st.info(
            "NPV = 0: Giá trị hiện tại dòng tiền thu vào bằng "
            "giá trị hiện tại dòng tiền chi ra."
        )

    if irr is not None:
        if irr > r:
            st.success(
                "IRR lớn hơn tỷ lệ chiết khấu: đây là dấu hiệu "
                "ủng hộ việc chấp nhận dự án theo tiêu chí IRR, "
                "nếu dòng tiền thông thường và IRR có nghiệm duy nhất."
            )
        elif irr < r:
            st.warning(
                "IRR thấp hơn tỷ lệ chiết khấu: dự án không đạt "
                "mức sinh lời yêu cầu theo tiêu chí IRR thông thường."
            )
        else:
            st.info("IRR bằng tỷ lệ chiết khấu.")
    else:
        st.warning(
            "Không tìm được IRR trong khoảng khảo sát. "
            "Dòng tiền có thể không có nghiệm IRR hoặc có nhiều nghiệm."
        )

    if pi is not None:
        if pi > 1:
            st.success("PI > 1: Giá trị hiện tại dòng tiền thu vào lớn hơn dòng tiền chi ra.")
        elif pi < 1:
            st.warning("PI < 1: Giá trị hiện tại dòng tiền thu vào nhỏ hơn dòng tiền chi ra.")
        else:
            st.info("PI = 1: Giá trị hiện tại dòng tiền thu vào bằng dòng tiền chi ra.")

    if pp is None:
        st.warning("PP: Dự án chưa hoàn vốn trong thời gian dự báo.")
    else:
        st.write(f"**Thời gian hoàn vốn PP:** {format_year(pp)}")

    if dpp is None:
        st.warning("DPP: Dự án chưa hoàn vốn có chiết khấu trong thời gian dự báo.")
    else:
        st.write(f"**Thời gian hoàn vốn DPP:** {format_year(dpp)}")

    # ======================================
    # BẢNG DÒNG TIỀN CHI TIẾT
    # ======================================
    st.subheader("6. Bảng dòng tiền và giá trị hiện tại")

    rows = []

    cumulative_cf = 0.0
    cumulative_pv = 0.0

    for t, cf in enumerate(full_cash_flows):
        discounted_cf = cf / (1 + r) ** t
        cumulative_cf += cf
        cumulative_pv += discounted_cf

        rows.append({
            "Năm": t,
            "Dòng tiền": round(cf, 4),
            "Hệ số chiết khấu": round(1 / (1 + r) ** t, 6),
            "Giá trị hiện tại": round(discounted_cf, 4),
            "Lũy kế dòng tiền": round(cumulative_cf, 4),
            "Lũy kế giá trị hiện tại": round(cumulative_pv, 4)
        })

    df = pd.DataFrame(rows)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    # ======================================
    # XUẤT FILE EXCEL / CSV
    # ======================================
    st.subheader("7. Xuất kết quả")

    csv_data = df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        label="⬇️ Tải bảng dòng tiền CSV",
        data=csv_data,
        file_name="phan_tich_dong_tien_du_an.csv",
        mime="text/csv",
        use_container_width=True
    )

    ket_qua = pd.DataFrame({
        "Chỉ tiêu": ["NPV", "IRR", "MIRR", "PI", "PP", "DPP"],
        "Kết quả": [
            f"{format_money(npv)} {don_vi_tien}",
            f"{irr * 100:.2f}%" if irr is not None else "Không xác định",
            f"{mirr * 100:.2f}%" if mirr is not None else "Không xác định",
            f"{pi:.4f}" if pi is not None else "Không xác định",
            format_year(pp),
            format_year(dpp)
        ]
    })

    st.download_button(
        label="⬇️ Tải bảng chỉ tiêu CSV",
        data=ket_qua.to_csv(index=False).encode("utf-8-sig"),
        file_name="ket_qua_phan_tich_du_an.csv",
        mime="text/csv",
        use_container_width=True
    )

# ==========================================
# 9. HƯỚNG DẪN CÔNG THỨC
# ==========================================
with st.expander("📘 Giải thích công thức các chỉ tiêu"):
    st.markdown(
        """
        **1. NPV – Giá trị hiện tại thuần**

        NPV = Tổng giá trị hiện tại của các dòng tiền,
        bao gồm vốn đầu tư ban đầu tại năm 0.

        **2. IRR – Tỷ suất hoàn vốn nội bộ**

        IRR là tỷ lệ chiết khấu làm cho NPV bằng 0.

        **3. MIRR – Tỷ suất hoàn vốn nội bộ điều chỉnh**

        MIRR xem xét chi phí tài trợ dòng tiền âm và tỷ lệ
        tái đầu tư dòng tiền dương.

        **4. PI – Chỉ số sinh lời**

        PI = Giá trị hiện tại của dòng tiền dương /
        Giá trị hiện tại của toàn bộ dòng tiền âm.

        **5. PP – Thời gian hoàn vốn**

        PP xác định thời gian cần thiết để dòng tiền tích lũy
        chưa chiết khấu bù đắp vốn đầu tư và các dòng tiền âm.

        **6. DPP – Thời gian hoàn vốn có chiết khấu**

        DPP xác định thời gian cần thiết để dòng tiền tích lũy
        sau chiết khấu bù đắp các khoản đầu tư.

        **Lưu ý:** Khi dòng tiền đổi dấu nhiều lần, IRR có thể
        có nhiều nghiệm hoặc không có nghiệm thực phù hợp.
        PI và thời gian hoàn vốn cũng cần được xem xét cùng NPV,
        đặc biệt khi so sánh các dự án loại trừ lẫn nhau.
        """
    )

st.caption(
    "Công cụ phục vụ học tập và phân tích sơ bộ. "
    "Kết quả phụ thuộc vào độ chính xác của dòng tiền và "
    "các giả định tài chính do người dùng nhập."
    )
