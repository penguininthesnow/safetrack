const API_BASE =
    window.location.hostname === "127.0.0.1" ||
        window.location.hostname === "localhost"
        ? "http://127.0.0.1:8000/api" // 本地
        : "https://penguinthesnow.com/api"; // 伺服器 