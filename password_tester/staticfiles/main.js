// External JS for Password Breach Analyzer
function togglePassword(inputId, checkbox) {
    const input = document.getElementById(inputId);
    input.type = checkbox.checked ? 'text' : 'password';
}

function suggestPassword() {
    const charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+[]{}";
    let password = "";
    for (let i = 0; i < 14; i++) {
        password += charset.charAt(Math.floor(Math.random() * charset.length));
    }
    const pwInput = document.getElementById('password');
    pwInput.value = password;
    if (typeof updateStrengthMeter === 'function') updateStrengthMeter();
}

function suggestComparePassword() {
    let charset = '';
    if (document.getElementById('opt_upper').checked) charset += 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    if (document.getElementById('opt_lower').checked) charset += 'abcdefghijklmnopqrstuvwxyz';
    if (document.getElementById('opt_num').checked) charset += '0123456789';
    if (document.getElementById('opt_sym').checked) charset += '!@#$%^&*()-_=+[]{}';
    let len = parseInt(document.getElementById('opt_len').value) || 14;
    if (!charset) charset = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    let password = '';
    for (let i = 0; i < len; i++) {
        password += charset.charAt(Math.floor(Math.random() * charset.length));
    }
    const pwInput = document.getElementById('compare_password');
    pwInput.value = password;
}

function checkBreach(password) {
    // This function should be implemented to handle breach check logic
}

function updateStrengthMeter() {
    const pw = document.getElementById('password').value;
    const bar = document.getElementById('strength-bar');
    const feedback = document.getElementById('strength-feedback');
    const policyList = document.getElementById('policy-list');
    const entropyDisplay = document.getElementById('entropy-display');
    if (window.zxcvbn) {
        const result = zxcvbn(pw);
        const score = result.score;
        const colors = ['#ff3333', '#ff9933', '#ffcc00', '#99ff33', '#39ff14'];
        bar.style.width = ((score + 1) * 20) + '%';
        bar.style.background = colors[score];
        const policies = [
            {ok: /[A-Z]/.test(pw), label: 'Uppercase'},
            {ok: /[a-z]/.test(pw), label: 'Lowercase'},
            {ok: /[0-9]/.test(pw), label: 'Number'},
            {ok: /[^A-Za-z0-9]/.test(pw), label: 'Symbol'}
        ];
        policyList.innerHTML = policies.map(p => `<li style='color:${p.ok ? '#39ff14':'#ff3333'}'>${p.ok ? '✔':'✖'} ${p.label}</li>`).join('');
        entropyDisplay.textContent = 'Entropy: ' + (result.entropy ? result.entropy.toFixed(2) : '0') + ' bits';
    } else {
        bar.style.width = '0';
        feedback.textContent = '';
        policyList.innerHTML = '';
        entropyDisplay.textContent = '';
    }
    checkBreach(pw);
}

function copyToClipboard(id) {
    const el = document.getElementById(id);
    if (!el) return;
    const text = el.value || el.textContent;
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(function() {
            showCopyToast();
        }, function() {
            fallbackCopy(text);
        });
    } else {
        fallbackCopy(text);
    }
}

function fallbackCopy(text) {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);
    showCopyToast();
}

function copyGenerated() {
    copyToClipboard('genpw');
}

function showCopyToast() {
    const toast = document.getElementById('copy-toast');
    if (!toast) return;
    toast.style.display = 'block';
    toast.style.opacity = 0.97;
    setTimeout(function() {
        toast.style.opacity = 0;
        setTimeout(function() {
            toast.style.display = 'none';
        }, 1800);
    }, 1200);
}
// Add any additional JS as needed
