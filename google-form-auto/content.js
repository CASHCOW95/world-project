// 구글폼 자동입력 핵심 로직
const fillGoogleForm = () => {
    console.log("🚀 구글폼 자동 입력을 시작합니다...");
    chrome.storage.local.get(null, (data) => {
        if (!data || Object.keys(data).length === 0) {
            console.warn("저장된 프로필 정보가 없습니다. 확장 프로그램 팝업에서 먼저 정보를 입력해주세요.");
            return;
        }

        document.querySelectorAll('[role="listitem"]').forEach(item => {
            const text = item.innerText.toLowerCase();
            let value = "";

            if (text.includes("telegram") || text.includes("텔레")) value = data.telegram;
            else if (text.includes("twitter") || text.includes("트위터")) value = data.twitter;
            else if (text.includes("wallet") || text.includes("evm") || text.includes("지갑")) value = data.evm;
            else if (text.includes("youtube") || text.includes("유튜브")) value = data.youtube;
            else if (text.includes("phone") || text.includes("전화") || text.includes("연락처")) value = data.phone;

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
        console.log("✅ 모든 항목 입력 완료!");
    });
};

// 1. 단축키 감지 로직 ( ` 키를 누르면 실행 )
window.addEventListener('keydown', (e) => {
    // ` 키 (Backtick, 숫자 1 왼쪽 키) 가 눌렸을 때
    if (e.key === '`') {
        fillGoogleForm();
    }
});

// 2. 파이썬 스텔스 신호 감지 로직 ( #auto 가 주소에 있으면 실행 )
if (window.location.hash.includes('auto')) {
    // 페이지 안정화를 위해 1.2초 후 실행
    setTimeout(fillGoogleForm, 1200);
}
