
// 巡檢區
async function createInspection() {
    const savedToken = localStorage.getItem("token");

    if (!savedToken) {
        openModal();
        return;
    }

    const location = document.getElementById("location").value.trim();

    // 監聽下拉式選單，顯示"其他"欄位
    let item = document.getElementById("item").value;
    const otherItem = document.getElementById("other_item").value.trim();

    if (item === "其他") {
        item = otherItem;
    }

    const description = document.getElementById("description").value.trim();

    if (!location || !item || !description) {
        alert("巡檢資料未填寫完整，請重新確認!");
        return;
    }

    const formData = new FormData();

    formData.append("date_value", document.getElementById("date").value);
    formData.append("location", location);
    formData.append("item", item);
    formData.append("description", description);

    formData.append(
        "is_abnormal",
        document.querySelector('input[name="abnormal"]:checked').value === "true"
    );
    formData.append("abnormal_count", 0);

    // 設定支援多張相片上傳
    const fileInput = document.getElementById("photo");

    for (let i = 0; i < fileInput.files.length; i++) {
        formData.append("files", fileInput.files[i]);
    }

    // 利用response 檢查回傳錯誤
    const response = await fetch(`${API_BASE}/inspections/`, {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${savedToken}`
        },
        body: formData
    });

    const data = await response.json();

    if (response.ok) {
        if (data.is_abnormal) {
            window.location.href =
                `inspection-success.html?number=${data.inspection_number}&abnormal=${data.is_abnormal}`;
        } else {
            window.location.href =
                `inspection-success.html?number=${data.inspection_number}&abnormal=${data.is_abnormal}`;
        }
    }

}

function gotoInspection() {
    const token = localStorage.getItem("token")

    if (!token) {
        openModal();
        return;
    }

    // 已登入 => 導向巡檢頁
    window.location.href = "inspection.html"
}

