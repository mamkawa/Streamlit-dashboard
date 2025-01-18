// タブ切り替え
document.querySelectorAll('.tab-btn').forEach(button => {
  button.addEventListener('click', () => {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    button.classList.add('active');
    
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    document.getElementById(`${button.dataset.tab}-tab`).classList.add('active');
  });
});

// 文字カウント機能
const countText = document.getElementById('countText');
function updateCount() {
  const text = countText.value;
  document.getElementById('totalCount').textContent = text.length;
  document.getElementById('noSpaceCount').textContent = text.replace(/\s/g, '').length;
  document.getElementById('noLineBreakCount').textContent = text.replace(/\n/g, '').length;
}
countText.addEventListener('input', updateCount);

// パスワード生成機能
document.getElementById('passwordLength').addEventListener('input', function(e) {
  document.getElementById('lengthValue').textContent = e.target.value;
});

document.getElementById('generate').addEventListener('click', generatePassword);
document.getElementById('copy').addEventListener('click', copyPassword);

function generatePassword() {
  const length = document.getElementById('passwordLength').value;
  const useUpper = document.getElementById('uppercase').checked;
  const useLower = document.getElementById('lowercase').checked;
  const useNumbers = document.getElementById('numbers').checked;
  const useSymbols = document.getElementById('symbols').checked;

  let chars = '';
  if (useUpper) chars += 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
  if (useLower) chars += 'abcdefghijklmnopqrstuvwxyz';
  if (useNumbers) chars += '0123456789';
  if (useSymbols) chars += '!@#$%^&*()_+-=[]{}|;:,.<>?';

  let password = '';
  for (let i = 0; i < length; i++) {
    password += chars.charAt(Math.floor(Math.random() * chars.length));
  }

  document.getElementById('passwordResult').value = password;
}

function copyPassword() {
  const passwordField = document.getElementById('passwordResult');
  passwordField.select();
  document.execCommand('copy');
}

// 文字変換機能
document.getElementById('toFullWidth').addEventListener('click', () => {
  const text = document.getElementById('convertText').value;
  const converted = text.replace(/[A-Za-z0-9]/g, s => String.fromCharCode(s.charCodeAt(0) + 0xFEE0));
  document.getElementById('convertResult').value = converted;
});

document.getElementById('toHalfWidth').addEventListener('click', () => {
  const text = document.getElementById('convertText').value;
  const converted = text.replace(/[Ａ-Ｚａ-ｚ０-９]/g, s => String.fromCharCode(s.charCodeAt(0) - 0xFEE0));
  document.getElementById('convertResult').value = converted;
}); 