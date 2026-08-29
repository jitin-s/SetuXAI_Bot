(function () {
  // Configurable API Backend URL: Defaults to window.SETUX_AI_API_URL or localhost:8000
  const SERVER_URL = (window.SETUX_AI_CONFIG && window.SETUX_AI_CONFIG.apiUrl) || "http://localhost:8000";
  const WIDGET_IFRAME_URL = (window.SETUX_AI_CONFIG && window.SETUX_AI_CONFIG.widgetUrl) || "http://localhost:5173";

  // 1. Auto-Scan Host Website Content & Send Payload to AI Backend
  function autoScanHostWebsite() {
    try {
      const pageData = {
        url: window.location.href,
        title: document.title || window.location.hostname,
        html: document.body ? document.body.innerText.substring(0, 8000) : ""
      };

      fetch(SERVER_URL + "/api/scan-website", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(pageData)
      }).then(res => res.json()).then(data => {
        console.log("[SetuX AI Widget] Successfully scanned & learned host website content:", data);
      }).catch(err => {
        console.warn("[SetuX AI Widget] Website auto-scan pending backend connection:", err);
      });
    } catch (e) {
      console.warn("[SetuX AI Widget] Auto-scan error:", e);
    }
  }

  // Execute Host Website Scan on Load
  if (document.readyState === "complete" || document.readyState === "interactive") {
    autoScanHostWebsite();
  } else {
    window.addEventListener("DOMContentLoaded", autoScanHostWebsite);
  }

  // 2. Inject Floating Support Widget Button & iFrame Popup
  const widgetContainer = document.createElement("div");
  widgetContainer.id = "setux-floating-widget-root";
  widgetContainer.innerHTML = `
    <style>
      #setux-floating-btn {
        position: fixed;
        bottom: 24px;
        right: 24px;
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: #1e3a8a;
        color: #ffffff;
        border: 3px solid #f59e0b;
        box-shadow: 0 8px 24px rgba(0,0,0,0.25);
        cursor: pointer;
        display: flex;
        justify-content: center;
        align-items: center;
        font-weight: bold;
        font-size: 22px;
        z-index: 999999;
        transition: transform 0.2s ease;
      }
      #setux-floating-btn:hover {
        transform: scale(1.08);
      }
      #setux-widget-popup {
        display: none;
        position: fixed;
        bottom: 96px;
        right: 24px;
        width: 420px;
        height: 620px;
        max-width: 90vw;
        max-height: 80vh;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 12px 36px rgba(0,0,0,0.3);
        z-index: 999998;
        border: 2px solid #1e3a8a;
        background: #ffffff;
      }
      #setux-widget-iframe {
        width: 100%;
        height: 100%;
        border: none;
      }
    </style>

    <div id="setux-floating-btn" title="Open SetuX Citizen Assistance Helpdesk">S</div>
    <div id="setux-widget-popup">
      <iframe id="setux-widget-iframe" src="${WIDGET_IFRAME_URL}"></iframe>
    </div>
  `;

  document.body.appendChild(widgetContainer);

  const btn = document.getElementById("setux-floating-btn");
  const popup = document.getElementById("setux-widget-popup");
  let isOpen = false;

  btn.addEventListener("click", function () {
    isOpen = !isOpen;
    popup.style.display = isOpen ? "block" : "none";
    btn.innerHTML = isOpen ? "✕" : "S";
  });
})();
