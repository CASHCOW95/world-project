document.addEventListener("DOMContentLoaded", async () => {
  const runBtn = document.querySelector("#run");
  if (!runBtn) return; // 🔥 조용히 종료 (에러 없음)

  runBtn.addEventListener("click", async () => {
    const data = {
      telegram: document.getElementById("telegram")?.value || "",
      twitter: document.getElementById("twitter")?.value || "",
      evm: document.getElementById("evm")?.value || "",
      youtube: document.getElementById("youtube")?.value || "",
      phone: document.getElementById("phone")?.value || ""
    };

    await chrome.storage.local.set(data);

    const [tab] = await chrome.tabs.query({
      active: true,
      currentWindow: true
    });

    if (!tab?.id) return;

    chrome.scripting.executeScript({
      target: { tabId: tab.id },
      args: [data],
      func: (data) => {
        document.querySelectorAll('[role="listitem"]').forEach(item => {
          const text = item.innerText.toLowerCase();
          let value = "";

          if (text.includes("telegram") || text.includes("텔레")) value = data.telegram;
          else if (text.includes("twitter") || text.includes("트위터")) value = data.twitter;
          else if (text.includes("wallet") || text.includes("evm") || text.includes("지갑")) value = data.evm;
          else if (text.includes("youtube") || text.includes("유튜브")) value = data.youtube;
          else if (text.includes("phone") || text.includes("전화")) value = data.phone;

          if (!value) return;

          const input =
            item.querySelector("input") ||
            item.querySelector("textarea") ||
            item.querySelector('[contenteditable="true"]');

          if (!input) return;

          input.focus();
          input.value = value;
          input.dispatchEvent(new Event("input", { bubbles: true }));
          input.dispatchEvent(new Event("change", { bubbles: true }));
          input.blur();
        });
      }
    });
  });
});
