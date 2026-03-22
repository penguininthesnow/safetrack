async function loadNotificationSettings() {
    const token = localStorage.getItem("token");

    const response = await fetch(`${API_BASE}/notification-settings`, {
        headers: {
            "Authorization": `Bearer ${token}`
        }
    });

    if (response.status === 403) {
        alert("沒有權限查看此畫面");
        location.href = "index.html";
        return;
    }

    if (!response.ok) {
        alert("載入通知設定失敗");
        return;
    }

    const data = await response.json();

    if (!data) return;

    document.getElementById("lineGroupName").value = data.line_group_name || "";
    document.getElementById("lineGroupId").value = data.line_group_id || "";
    document.getElementById("notifyAbnormal").value = String(data.notify_abnormal);
    document.getElementById("isEnabled").value = String(data.is_enabled);
}

async function saveNotificationSettings() {
    const token = localStorage.getItem("token");

    const body = {
        line_group_name: document.getElementById("lineGroupName").value,
        line_group_id: document.getElementById("lineGroupId").value,
        notify_abnormal: document.getElementById("notifyAbnormal").value === "true",
        is_enabled: document.getElementById("isEnabled").value === "true"
    };

    const response = await fetch(`${API_BASE}/notification-settings`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify(body)
    });

    const result = await response.json();

    if (!response.ok) {
        alert(result.detail || "儲存失敗");
        return;
    }

    alert(result.message || "通知設定已更新");
}

document.addEventListener("DOMContentLoaded", loadNotificationSettings);