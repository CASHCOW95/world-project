document.addEventListener('DOMContentLoaded', () => {
    // 로그인 체크 안 하고 바로 메인 화면 보여주기
    showMain(); 
});

document.getElementById('convertBtn').addEventListener('click', () => {
    const html = document.getElementById('htmlInput').value;
    if (!html) return alert('입력된 내용이 없습니다.');

    const tempArea = document.getElementById('tempArea');
    tempArea.innerHTML = html;

    const range = document.createRange();
    range.selectNode(tempArea);
    window.getSelection().removeAllRanges();
    window.getSelection().addRange(range);

    try {
        document.execCommand('copy');
        alert('변환 완료! 블로그에 붙여넣기 하세요.');
    } catch (err) {
        alert('복사 실패');
    }
    window.getSelection().removeAllRanges();
});

function showMain() {
    document.getElementById('loginSection').classList.add('hidden');
    document.getElementById('mainSection').classList.remove('hidden');
}