// welcome區塊
document.addEventListener("DOMContentLoaded", () => {
    const track = document.getElementById("carouselTrack");
    const dots = document.querySelectorAll(".dot");

    if (!track || dots.length === 0) return;

    const slides = document.querySelectorAll(".carousel-slide");
    const firstClone = slides[0].cloneNode(true);
    track.appendChild(firstClone);

    let currentIndex = 0;
    let isTransitioning = false;
    const totalRealSlides = slides.length;

    function updateDots(index) {
        dots.forEach(dot => dot.classList.remove("active"));
        dots[index].classList.add("active");
    }

    function moveToSlide(index, withTransition = true) {
        if (withTransition) {
            track.style.transition = "transform 0.6s ease-in-out";
        } else {
            track.style.transition = "none";
        }

        track.style.transform = `translateX(-${index * 100}%)`;
    }

    function nextSlide() {
        if (isTransitioning) return;

        isTransitioning = true;
        currentIndex++;
        moveToSlide(currentIndex);

        if (currentIndex < totalRealSlides) {
            updateDots(currentIndex);
        } else {
            updateDots(0);
        }
    }

    track.addEventListener("transitionend", () => {
        if (currentIndex === totalRealSlides) {
            moveToSlide(0, false);
            currentIndex = 0;
        }
        isTransitioning = false;
    });

    dots.forEach((dot, index) => {
        dot.addEventListener("click", () => {
            if (isTransitioning) return;
            currentIndex = index;
            moveToSlide(currentIndex);
            updateDots(currentIndex);
        });
    });

    setInterval(nextSlide, 5000);
});


// 公佈欄區塊
async function loadOshaBulletin() {
    const container = document.getElementById("osha-list");

    if (!container) return;

    try {
        const res = await fetch(`${API_BASE}/osha/bulletin`);
        if (!res.ok) {
            throw new Error("載入失敗");
        }

        const data = await res.json();

        if (!data.items || data.items.length === 0) {
            container.innerHTML = "<p>目前沒有資料</p>";
            return;
        }

        let html = "<ul class='osha-items'>";
        data.items.forEach(item => {
            html += `
                <li>
                    <a href="${item.url}" target="_blank" rel="noopener noreferrer">
                        ${item.title}
                    </a>
                </li>
            `;
        });
        html += "</ul>";

        if (data.more_url) {
            html += `
                <div class="osha-more">
                    <a href="${data.more_url}" target="_blank" rel="noopener noreferrer">
                        查看更多公布欄
                    </a>
                </div>
            `;
        }

        container.innerHTML = html;
    } catch (error) {
        container.innerHTML = "<p>職安署公布欄載入失敗</p>";
        console.error("loadOshaBulletin error:", error);
    }
}

loadOshaBulletin();


// ==============使用流程教學區塊 =========================
document.addEventListener("DOMContentLoaded", () => {
    const steps = document.querySelectorAll(".guide-step");
    const lineFills = document.querySelectorAll(".step-line-fill");
    const guideTitle = document.getElementById("guideTitle");
    const guideDescription = document.getElementById("guideDescription");
    const guideVideo = document.getElementById("guideVideo");
    const guideVideoSource = document.getElementById("guideVideoSource");
    const guideBoard = document.querySelector(".guide-board");

    const guideData = [
        {
            title: "Step 1 | 登入 / 註冊",
            description: "使用者可先完成註冊或登入，進入系統後才能使用巡檢建立、通知設定與歷史紀錄查詢等功能。",
            video: "https://d336p3arlssoc.cloudfront.net/videos/step1.mp4"
        },
        {
            title: "Step 2｜會員設定與身分說明",
            description: "在會員設定中可查看基本資料，並依照帳號身分區分為主管或現場人員，不同角色可使用的功能權限也會有所不同。",
            video: "https://d336p3arlssoc.cloudfront.net/videos/step2.mp4"
        },
        {
            title: "Step 3｜通知設定",
            description: "使用者可設定通知方式，當巡檢紀錄出現異常時，系統可依設定自動發送提醒，提高異常處理效率。",
            video: "https://d336p3arlssoc.cloudfront.net/videos/step3.mp4"
        },
        {
            title: "Step 4｜填寫巡檢紀錄與 LINE 通知",
            description: "現場人員可建立巡檢紀錄，填寫地點、項目、說明與上傳圖片；若有異常，系統可即時發送 LINE 通知給相關人員。",
            video: "https://d336p3arlssoc.cloudfront.net/videos/step4.mp4"
        },
        {
            title: "Step 5｜查看歷史紀錄與管理功能",
            description: "使用者可查詢歷史巡檢紀錄，並進行預覽、修改、刪除，也能將資料下載成 CSV 檔，方便後續統計與管理。",
            video: "https://d336p3arlssoc.cloudfront.net/videos/step5.mp4"
        }
    ];

    let currentStep = 0;
    let hasStartedGuideVideo = false;

    function resetLines() {
        lineFills.forEach(fill => {
            fill.style.width = "0%";
        });
    }

    function updateDoneSteps(stepIndex) {
        steps.forEach((step, index) => {
            step.classList.remove("active", "done");

            if (index < stepIndex) {
                step.classList.add("done");
            } else if (index === stepIndex) {
                step.classList.add("active");
            }
        });

        lineFills.forEach((fill, index) => {
            if (index < stepIndex) {
                fill.style.width = "100%";
            } else if (index > stepIndex) {
                fill.style.width = "0%";
            }
        });
    }


    function updateGuide(stepIndex, shouldAutoPlay = true) {
        const data = guideData[stepIndex];

        currentStep = stepIndex;
        updateDoneSteps(stepIndex);

        guideTitle.textContent = data.title;
        guideDescription.textContent = data.description;

        guideVideo.pause();
        guideVideoSource.src = data.video;
        guideVideo.load();

        if (shouldAutoPlay) {
            guideVideo.play().catch(() => { });
        }
    }

    function nextGuideStep() {
        const nextStep = (currentStep + 1) % guideData.length;
        updateGuide(nextStep, true);
    }

    // 影片播放時，讓當前線條跟著進度跑
    guideVideo.addEventListener("timeupdate", () => {
        if (currentStep < lineFills.length && guideVideo.duration) {
            const progress = (guideVideo.currentTime / guideVideo.duration) * 100;
            lineFills[currentStep].style.width = `${progress}%`;
        }
    });

    // 影片播完自動跳下一步
    guideVideo.addEventListener("ended", () => {
        if (currentStep < lineFills.length) {
            lineFills[currentStep].style.width = "100%";
        }
        nextGuideStep();
    });

    // 點 step 手動切換
    steps.forEach((step, index) => {
        step.addEventListener("click", () => {
            hasStartedGuideVideo = true;
            updateGuide(index, true);
        });
    });

    resetLines();
    updateGuide(0, false);

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !hasStartedGuideVideo) {
                hasStartedGuideVideo = true;
                guideVideo.play().catch(() => { });
            }
        });
    }, {
        threshold: 0.9
    });

    if (guideBoard) {
        observer.observe(guideBoard);
    }
});

