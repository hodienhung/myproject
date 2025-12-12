document.addEventListener("DOMContentLoaded", function () {
    const popup = document.getElementById("popup");
    const popupContent = document.querySelector(".popup-content");
    const closeBtn = document.getElementById("closePopup");
    const gioiThieuBtn = document.getElementById("gioiThieuBtn");

    // 🟢 Hàm tạo bong bóng
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

    // 🟢 Mở popup
    function openPopup() {
        popup.style.display = "flex";
        createBubbles();
    }

    // 🔵 Tự bật khi vào trang
    openPopup();

    // 🔵 Nhấn Giới thiệu
    if (gioiThieuBtn) {
        gioiThieuBtn.addEventListener("click", function (e) {
            e.preventDefault();
            openPopup();
        });
    }

    // 🔴 Đóng bằng nút X
    closeBtn.addEventListener("click", function () {
        popup.style.display = "none";
    });

    // 🔴 Nhấn ra ngoài popup → đóng
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

                // ✅ Bỏ chọn tất cả checkbox khi ẩn
                comboOptions.querySelectorAll("input[type='checkbox']").forEach(cb => cb.checked = false);
            }
        });
    }
    function autoFormatDateTime(input) {
    let val = input.value.replace(/\D/g, ""); // bỏ hết ký tự không phải số

    if (val.length > 4) val = val.slice(0, 4) + "-" + val.slice(4);
    if (val.length > 7) val = val.slice(0, 7) + "-" + val.slice(7);
    if (val.length > 10) val = val.slice(0, 10) + " " + val.slice(10);
    if (val.length > 13) val = val.slice(0, 13) + ":" + val.slice(13);

    input.value = val.slice(0, 16); // giới hạn độ dài
}

document.getElementById("start_datetime").addEventListener("input", function() {
    autoFormatDateTime(this);
});

document.getElementById("end_datetime").addEventListener("input", function() {
    autoFormatDateTime(this);
});

});
