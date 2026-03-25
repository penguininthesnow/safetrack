
// sidebar互動
function openSidebar() {
    const sidebar = document.getElementById("sidebar");
    const overlay = document.getElementById("sidebarOverlay");
    const tag = document.getElementById("tag");

    if (!sidebar || !overlay || !tag) return;

    sidebar.style.display = "block";
    sidebar.style.left = "0";
    overlay.style.display = "block";
    tag.style.display = "none";
}

function closeSidebar() {
    const sidebar = document.getElementById("sidebar");
    const overlay = document.getElementById("sidebarOverlay");
    const tag = document.getElementById("tag");

    if (!sidebar || !overlay || !tag) return;

    sidebar.style.left = "-260px";
    overlay.style.display = "none";
    tag.style.display = "block";

    setTimeout(() => {
        sidebar.style.display = "none";
    }, 300);
}

// 專門控制首頁sidebar登入時才出現的
function toggleSidebarByLogin() {
    const token = localStorage.getItem("token");

    const tag = document.getElementById("tag");
    const sidebar = document.getElementById("sidebar");
    const overlay = document.getElementById("sidebarOverlay");
    const logoutArea = document.getElementById("logoutArea");

    if (!tag || !sidebar || !overlay) return;

    if (token) {
        // 有登入才顯示漢堡、顯示登出區塊
        tag.style.display = "block";
        if (logoutArea) logoutArea.style.display = "block";
    } else {
        // 沒登入就全部隱藏
        tag.style.display = "none";
        sidebar.style.display = "none";
        overlay.style.display = "none";
        if (logoutArea) logoutArea.style.display = "none";
    }
}

// 通知設定用 + 使用者身分判斷
async function loadCurrentUserForSidebar() {
    const token = localStorage.getItem("token");

    const notificationMenu = document.getElementById("notificationSettingMenu");
    const logoutArea = document.getElementById("logoutArea");

    toggleSidebarByLogin();


    console.log("sidebar token:", token);

    if (!token) return;

    try {
        const response = await fetch(`${API_BASE}/users/member`, {
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        console.log("sidebar response_status:", response.status);

        if (!response.ok) {
            localStorage.removeItem("token");
            toggleSidebarByLogin();

            if (notificationMenu) notificationMenu.style.display = "none";
            if (logoutArea) logoutArea.style.display = "none";
            return;
        }

        const user = await response.json();
        console.log("sidebar user:", user);

        // 登入成功後顯示登出區
        if (logoutArea) logoutArea.style.display = "block";

        // 只有 admin 顯示通知設定
        if (user.role === "admin") {
            if (notificationMenu) notificationMenu.style.display = "flex";
        } else {
            if (notificationMenu) notificationMenu.style.display = "none";
        }
    } catch (err) {
        console.error("載入使用者資料失敗", err);
    }
}

// 巡檢系統
function handleInspectionClick(event) {
    event.stopPropagation();

    const token = localStorage.getItem("token");
    if (!token) {
        closeSidebar();
        openModal();
        return;
    }
    //已登入 => 展開子選單
    const parent = event.target.closest(".menu-item");
    parent.classList.toggle("open");
}
// 建立巡檢資料
function goCreateInspection(event) {
    event.preventDefault();
    event.stopPropagation();

    const token = localStorage.getItem("token");

    if (!token) {
        closeSidebar();
        openModal();
        return;
    }
    window.location.href = "inspection.html";
}
// 查詢歷史紀錄
function goHistoryPage(event) {
    event.preventDefault();
    event.stopPropagation();

    const token = localStorage.getItem("token");
    if (!token) {
        closeSidebar();
        openModal();
        return;
    }
    window.location.href = "inspection-history.html";
}


// sidebar 專用資料
async function loadSidebarYears() {
    try {
        const response = await fetch(`${API_BASE}/inspections/years`);
        const years = await response.json();

        const container = document.getElementById("yearList");
        container.innerHTML = "";

        years.forEach(year => {
            const link = document.createElement("a");

            link.href = `inspection-history.html?year=${year}`;
            link.textContent = `${year} 年`;

            container.appendChild(link);
        });
    } catch (err) {
        console.error("載入年份失敗", err);
    }
}

document.addEventListener("DOMContentLoaded", () => {
    toggleSidebarByLogin();

    const container = document.getElementById("yearList");
    if (container) {
        loadSidebarYears();
    }
    loadCurrentUserForSidebar();
});