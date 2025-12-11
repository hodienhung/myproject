document.addEventListener("DOMContentLoaded", function () {
    const serviceSelect = document.getElementById("serviceSelect");
    const comboBox = document.getElementById("comboOptions");

    serviceSelect.addEventListener("change", function () {
        comboBox.style.display =
            serviceSelect.value === "combo-tuy-chon" ? "block" : "none";
    });
});
