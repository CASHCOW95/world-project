function createButton() {
  const container =
    document.querySelector('[role="main"]') ||
    document.body;

  if (!container) return;

  // 이미 버튼 있으면 또 안 만듦
  if (document.getElementById('autoFillBtn')) return;

  const button = document.createElement('button');
  button.id = 'autoFillBtn';
  button.innerText = '🦝 자동 입력';

  button.style.position = 'fixed';
  button.style.bottom = '24px';
  button.style.right = '24px';
  button.style.zIndex = '2147483647'; // 🔥 제일 중요
  button.style.padding = '12px 16px';
  button.style.background = '#1a73e8';
  button.style.color = '#fff';
  button.style.border = 'none';
  button.style.borderRadius = '8px';
  button.style.cursor = 'pointer';
  button.style.fontSize = '14px';

  button.onclick = () => {
    alert('🦝 자동 입력 버튼 클릭됨');
  };

  container.appendChild(button);
}

// iframe 안에서만 실행
if (window.self !== window.top) {
  setTimeout(createButton, 1000);
}
