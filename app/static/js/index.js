document.addEventListener("DOMContentLoaded", function () {
    const popup = document.getElementById("popup");
    const popupContent = document.querySelector(".popup-content");
    const closeBtn = document.getElementById("closePopup");
    const gioiThieuBtn = document.getElementById("gioiThieuBtn");

    function createBubbles() {
        const bubbleContainer = document.createElement("div");
        bubbleContainer.classList.add("bubble-container");
        popup.appendChild(bubbleContainer);

        for (let i = 0; i < 20; i++) {
            const bubble = document.createElement("span");
            bubble.classList.add("bubble");

            const size = Math.random() * 20 + 10;
            bubble.style.width = `${size}px`;
            bubble.style.height = `${size}px`;
            bubble.style.left = `${Math.random() * 100}%`;
            bubble.style.animationDuration = `${Math.random() * 2 + 2}s`;

            bubbleContainer.appendChild(bubble);
            setTimeout(() => bubble.remove(), 4000);
        }
    }

    function openPopup() {
        popup.style.display = "flex";
        createBubbles();
    }

    openPopup();

    if (gioiThieuBtn) {
        gioiThieuBtn.addEventListener("click", function (e) {
            e.preventDefault();
            openPopup();
        });
    }

    closeBtn.addEventListener("click", function () {
        popup.style.display = "none";
    });

    popup.addEventListener("click", function (e) {
        if (!popupContent.contains(e.target)) {
            popup.style.display = "none";
        }
    });

    const serviceSelect = document.querySelector("select[name='service']");
    const comboOptions = document.getElementById("comboOptions");

    if (serviceSelect) {
        serviceSelect.addEventListener("change", function () {
            if (this.value === "combo-tuy-chon") {
                comboOptions.style.display = "block";
            } else {
                comboOptions.style.display = "none";
                comboOptions.querySelectorAll("input[type='checkbox']").forEach(cb => cb.checked = false);
            }
        });
    }

    // ============================
    //  AUTO FORMAT DATETIME
    // ============================
    function autoFormatDateTime(input) {
        let val = input.value.replace(/\D/g, "");

        if (val.length > 4) val = val.slice(0, 4) + "-" + val.slice(4);
        if (val.length > 7) val = val.slice(0, 7) + "-" + val.slice(7);
        if (val.length > 10) val = val.slice(0, 10) + " " + val.slice(10);
        if (val.length > 13) val = val.slice(0, 13) + ":" + val.slice(13);

        // ====== TỰ THÊM SỐ 0 TRƯỚC GIỜ VÀ PHÚT ======
        let parts = val.split(" ");

        if (parts.length === 2) {
            let time = parts[1];

            // Auto zero hour (input "1" → "01")
            if (time.length === 1 && Number(time) < 10) {
                time = "0" + time;
            }

            // Auto zero minute (input "01:3" → "01:03")
            if (time.length === 3 && time[2] !== ":") {
                let hh = time.slice(0, 2);
                let mm = time.slice(2);
                if (Number(mm) < 10) mm = "0" + mm;
                time = hh + ":" + mm;
            }

            parts[1] = time;
        }

        input.value = val.slice(0, 16);
    }

    const startInput = document.getElementById("start_datetime");
    const endInput = document.getElementById("end_datetime");

    startInput.addEventListener("input", function () {
        autoFormatDateTime(this);
        validateDateTime(this);
        validateOrder();
    });

    endInput.addEventListener("input", function () {
        autoFormatDateTime(this);
        validateDateTime(this);
        validateOrder();
    });

    // ============================
    //   VALIDATE DATETIME
    // ============================
    function ensureErrorElement(input) {
        const errorId = input.id + "_error";
        let errorEl = document.getElementById(errorId);

        if (!errorEl) {
            errorEl = document.createElement("div");
            errorEl.id = errorId;
            errorEl.style.color = "red";
            errorEl.style.fontSize = "13px";
            errorEl.style.marginTop = "3px";
            input.parentNode.appendChild(errorEl);
        }
        return errorEl;
    }

    function validateDateTime(input) {
        const errorEl = ensureErrorElement(input);

        const val = input.value.trim();
        if (!val) {
            errorEl.textContent = "⚠ Vui lòng nhập ngày giờ";
            return false;
        }

        const regex = /^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$/;
        if (!regex.test(val)) {
            errorEl.textContent = "⚠ Định dạng phải là YYYY-MM-DD HH:MM";
            return false;
        }

        const [date, time] = val.split(" ");
        const [yyyy, mm, dd] = date.split("-").map(Number);
        const [hh, min] = time.split(":").map(Number);

        if (mm < 1 || mm > 12) {
            errorEl.textContent = "⚠ Tháng không hợp lệ";
            return false;
        }

        const daysInMonth = new Date(yyyy, mm, 0).getDate();
        if (dd < 1 || dd > daysInMonth) {
            errorEl.textContent = `⚠ Ngày không hợp lệ (tháng ${mm} chỉ có ${daysInMonth} ngày)`;
            return false;
        }

        if (hh < 0 || hh > 23) {
            errorEl.textContent = "⚠ Giờ phải từ 00 đến 23";
            return false;
        }

        if (min < 0 || min > 59) {
            errorEl.textContent = "⚠ Phút phải từ 00 đến 59";
            return false;
        }

        errorEl.textContent = "";
        return true;
    }

    function parseToDate(val) {
        const regex = /^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2})$/;
        const m = val.match(regex);
        if (!m) return null;
        const [_, y, mo, d, h, mi] = m;
        return new Date(Number(y), Number(mo) - 1, Number(d), Number(h), Number(mi));
    }

    // ============================
    //   VALIDATE ORDER
    // ============================
    function validateOrder() {
        const startVal = startInput.value.trim();
        const endVal = endInput.value.trim();
        const endErrorEl = ensureErrorElement(endInput);

        if (!/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$/.test(startVal) ||
            !/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$/.test(endVal)) {
            endErrorEl.textContent = "";
            return true;
        }

        const startDate = parseToDate(startVal);
        const endDate = parseToDate(endVal);

        if (endDate <= startDate) {
            endErrorEl.textContent = "⚠ Thời gian kết thúc phải sau thời gian bắt đầu";
            return false;
        }

        endErrorEl.textContent = "";
        return true;
    }

    // ============================
    //   CHẶN SUBMIT NẾU LỖI
    // ============================
    const form = document.querySelector("form");

    form.addEventListener("submit", function (e) {
        const validStart = validateDateTime(startInput);
        const validEnd = validateDateTime(endInput);
        const orderOk = validateOrder();

        if (!validStart || !validEnd || !orderOk) {
            e.preventDefault();
            alert("❌ Vui lòng sửa lỗi ngày giờ trước khi gửi!");
            return false;
        }

        return true;
    });
});
