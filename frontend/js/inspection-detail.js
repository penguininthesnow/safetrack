document.addEventListener("DOMContentLoaded", () => {
    loadInspection()
})

function getQueryParam(name) {
    const params = new URLSearchParams(window.location.search)
    return params.get(name)
}

function setText(id, value) {

    const el = document.getElementById(id)

    if (el) {
        el.innerText = value
    }

}

async function loadInspection() {

    const number = getQueryParam("number")

    if (!number) {
        alert("找不到巡檢紀錄")
        return
    }

    try {
        const response = await fetch(
            `${API_BASE}/inspections/number/${number}`
        )

        if (!response.ok) {
            throw new Error("API錯誤")
        }

        const data = await response.json()

        console.log("inspection data:", data)

        setText("inspectionNumber", data.inspection_number)
        setText("date", data.date)
        setText("location", data.location)
        setText("item", data.item)
        setText("description", data.description)
        setText("abnormal", data.is_abnormal ? "是 ⚠" : "否")


        if (data.image_url) {
            const images = data.image_url.split(",");
            const container = document.getElementById("image_container")

            // Lightbox 功能
            const lightbox = document.getElementById("lightbox");
            const lightboxImg = document.getElementById("lightbox-img");
            const closeBtn = document.getElementById("lightbox-close");

            images.forEach(url => {
                const img = document.createElement("img")

                img.src = url
                img.alt = "巡檢圖片"
                img.style.display = "block";
                img.style.maxWidth = "100%";
                img.style.marginTop = "10px";
                img.style.borderRadius = "8px";

                // 點圖片打開 Lightbox
                if (lightbox && lightboxImg) {
                    img.addEventListener("click", () => {
                        lightboxImg.src = img.src;
                        lightbox.classList.add("show");
                    });
                }

                container.appendChild(img);
            });

            // 點 × 或背景關閉
            if (closeBtn && lightbox) {
                closeBtn.addEventListener("click", () => lightbox.classList.remove("show"));
                lightbox.addEventListener("click", (e) => {
                    if (e.target === lightbox) lightbox.classList.remove("show");
                });
            }

        } else {
            console.warn("沒有 image_url");
        }

    } catch (error) {
        console.error("取得巡檢資料失敗", error);
        alert("讀取巡檢紀錄失敗");
    }
}

