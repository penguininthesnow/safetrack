
let token = null;

// const API_BASE = "http://127.0.0.1:8000";  // 開發用
// const API_BASE = "https://penguinthesnow.com";  // 正式用

async function submitAuth() {
    const email = document.getElementById("modalEmail").value.trim();
    const password = document.getElementById("modalPassword").value.trim();

    // 會員註冊
    if (authMode === "register") {
        const username = document.getElementById("modalUsername").value.trim();

        if (!username || !email || !password) {
            alert("註冊資料未填寫完整，請重新確認!");
            return;
        }

        const response = await fetch(`${API_BASE}/users/register`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                username: username,
                email: email,
                password: password,
                role: "users"
            })
        });
        if (response.ok) {
            alert("註冊成功，請重新登入!");
            toggleMode();
        } else {
            alert("已有註冊過，註冊失敗，請重新註冊。");
        }
    }
    else {
        if (!email || !password) {
            alert("資料未填寫完整，請重新確認!");
            return;
        }
        // 登入驗證部分
        const formData = new URLSearchParams();
        formData.append("username", email);
        formData.append("password", password);

        const response = await fetch(`${API_BASE}/users/login`, {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            localStorage.setItem("token", data.access_token);
            localStorage.setItem("email", email);

            //  呼叫 member API 拿使用者資料
            await fetchUserInfo();
            alert("登入成功!");

            closeModal();
            updateUserUI();

            window.location.href = "index.html"
        } else {
            alert("帳號或密碼錯誤");
        }
    }
}
// fetchUserInfo 登入時使用者名稱顯示
async function fetchUserInfo() {
    const token = localStorage.getItem("token");

    const response = await fetch(`${API_BASE}/users/member`, {
        method: "GET",
        headers: {
            "Authorization": `Bearer ${token}`
        }
    });

    if (response.ok) {
        const user = await response.json();

        localStorage.setItem("username", user.username);
        localStorage.setItem("email", user.email);
    }
}

// 登出
async function logout() {
    const token = localStorage.getItem("token");

    if (token) {
        try {
            await fetch(`${API_BASE}/users/logout`, {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            });
        } catch (error) {
            console.log("Logout API error:", error);
        }
    }

    localStorage.removeItem("token");
    localStorage.removeItem("email");
    localStorage.removeItem("username");

    resetModal();
    closeModal();
    updateUserUI();
    closeSidebar(); // 登出時選單收起來

    // 延遲一下讓動畫跑完
    setTimeout(() => {
        window.location.href = "index.html";
    }, 200);

    alert("已登出~");
}

function resetModal() {
    authMode = "login";

    document.getElementById("modalTitle").innerText = "會員登入";

    document.getElementById("modalEmail").style.display = "block";
    document.getElementById("modalPassword").style.display = "block";
    document.getElementById("usernameField").style.display = "none";

    document.querySelector(".modal button").style.display = "block";
    // document.querySelector("close-btn").style.display = "block";

    document.getElementById("switchText").innerText = "還沒有帳號?";
    document.querySelector(".modal a").innerText = "點此註冊";
    document.querySelector(".modal a").onclick = toggleMode;
}

let authMode = "login";
function openModal() {
    document.getElementById("modalbackdrop").style.display = "block";
    document.getElementById("authmodal").style.display = "block";

    const email = localStorage.getItem("email");

    if (email) {
        document.getElementById("modalTitle").innerText = "會員中心";

        // 隱藏登入欄位
        document.getElementById("modalEmail").style.display = "block";
        document.getElementById("modalPassword").style.display = "block";
        document.getElementById("usernameField").style.display = "none";

        document.querySelector(".modal button").style.display = "none";
        // document.querySelector(".close-btn").style.display = "none";

        document.getElementById("switchText").innerText = "";
        const link = document.querySelector(".modal a");
        link.innerText = "登出";
        link.onclick = logout;
    }

}

function closeModal() {
    document.getElementById("modalbackdrop").style.display = "none";
    document.getElementById("authmodal").style.display = "none";
}

function toggleMode() {
    if (authMode === "login") {
        authMode = "register";
        document.getElementById("modalTitle").innerText = "會員註冊";
        document.getElementById("switchText").innerText = "已有帳號?";
        document.querySelector(".modal a").innerText = "點此登入";

        document.getElementById("usernameField").style.display = "block";
    } else {
        authMode = "login"
        document.getElementById("modalTitle").innerText = "會員登入";
        document.getElementById("switchText").innerText = "還沒有帳號?";
        document.querySelector(".modal a").innerText = "點此註冊";

        document.getElementById("usernameField").style.display = "none";
    }
}

function updateUserUI() {
    const email = localStorage.getItem("email");
    const username = localStorage.getItem("username");
    const userArea = document.getElementById("userArea");
    const switchText = document.getElementById("switchText");
    const switchLink = document.querySelector(".modal a");
    const token = localStorage.getItem("token");
    const logoutArea = document.getElementById("logoutArea");

    if (username) {
        if (userArea) {
            userArea.innerText = username + "，您好";
        }

        if (switchText) {
            switchText.innerText = "";
        }

        if (switchLink) {
            switchLink.innerText = "登出";
            switchLink.onclick = logout;
        }
    } else {
        if (userArea) {
            userArea.innerHTML =
                '<img src="images/sign_1.png" width="30" height="30">';
        }

        if (switchText) {
            switchText.innerText = "還沒有帳號?";
        }

        if (switchLink) {
            switchLink.innerText = "點此註冊";
            switchLink.onclick = toggleMode;
        }
    }

    if (logoutArea) {
        logoutArea.style.display = token ? "block" : "none";
    }
}

// 刷新頁面
window.onload = async function () {
    const token = localStorage.getItem("token");
    if (token && !localStorage.getItem("username")) {
        await fetchUserInfo();
    }
    updateUserUI();
};

document.addEventListener("DOMContentLoaded", function () {
    const token = localStorage.getItem("token");

    if (window.location.pathname.includes("inspection.html") && !token) {
        window.location.href = "index.html";
    }
});

function homepage() {
    window.location.href = "index.html";
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