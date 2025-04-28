import time
import math
import re
from zxcvbn import zxcvbn
import pwnedpasswords
import requests

# Helper: entropy calculation
def calculate_entropy(password):
    charset = 0
    if re.search(r'[a-z]', password):
        charset += 26
    if re.search(r'[A-Z]', password):
        charset += 26
    if re.search(r'[0-9]', password):
        charset += 10
    if re.search(r'[^a-zA-Z0-9]', password):
        charset += 32  # Approximation for symbols
    if charset == 0:
        return 0
    entropy = len(password) * math.log2(charset)
    return round(entropy, 2)

# Helper: keyboard patterns
KEYBOARD_PATTERNS = [
    '12345', 'qwerty', 'asdf', 'zxcv', 'password', 'letmein', 'admin', 'welcome', 'passw0rd', 'qazwsx', 'iloveyou'
]
def check_keyboard_patterns(password):
    pw_lower = password.lower()
    found = [p for p in KEYBOARD_PATTERNS if p in pw_lower]
    return found

# Helper: leet speak dictionary check
LEET_MAP = {'4':'a','@':'a','3':'e','1':'i','!':'i','0':'o','$':'s','5':'s','7':'t'}
def leet_to_plain(password):
    pw = password.lower()
    for k, v in LEET_MAP.items():
        pw = pw.replace(k, v)
    return pw

def check_leet_dictionary(password, common_words):
    pw_plain = leet_to_plain(password)
    found = [w for w in common_words if w in pw_plain]
    return found

# Helper: brute-force time estimate
def brute_force_time(password):
    charset = 0
    if re.search(r'[a-z]', password):
        charset += 26
    if re.search(r'[A-Z]', password):
        charset += 26
    if re.search(r'[0-9]', password):
        charset += 10
    if re.search(r'[^a-zA-Z0-9]', password):
        charset += 32
    guesses = charset ** len(password)
    guesses_per_sec = 1e9  # 1 billion guesses/sec (fast GPU)
    seconds = guesses / guesses_per_sec
    return seconds

# Load common words for dictionary/leet checks
import os
COMMON_WORDS_PATH = os.path.join(os.path.dirname(__file__), 'pwdchecker', 'common_passwords.txt')
try:
    with open(COMMON_WORDS_PATH, 'r', encoding='utf-8') as f:
        COMMON_WORDS = set(line.strip().lower() for line in f if line.strip())
except Exception:
    COMMON_WORDS = set()

def check_password_strength(password, deep=False, custom_dict=None):
    results = {
        'zxcvbn_result': None,
        'hibp_count': None,
        'entropy': None,
        'keyboard_patterns': [],
        'leet_matches': [],
        'brute_force_seconds': None,
        'brute_force_minutes': None,
        'brute_force_hours': None,
        'brute_force_days': None,
        'brute_force_years': None,
        'steps': [],
        'error': None,
        'extra_checks': [],
        'custom_dict_matches': [],
    }
    steps = results['steps']

    steps.append('> [*] Analyzing password...')

    # 1. Check strength using zxcvbn
    try:
        start_time = time.time()
        zxcvbn_analysis = zxcvbn(password)
        end_time = time.time()
        zxcvbn_analysis['calc_time'] = (end_time - start_time) * 1000
        results['zxcvbn_result'] = zxcvbn_analysis
        entropy = calculate_entropy(password)
        results['entropy'] = entropy
        steps.append('> [*] zxcvbn analysis complete.')
    except Exception as e:
        results['error'] = f"Error during zxcvbn analysis: {e}"
        steps.append(f"> [!] zxcvbn analysis error: {e}")

    # 2. Entropy calculation
    steps.append(f"> [*] Entropy calculated: {results['entropy']} bits.")

    # 3. Keyboard patterns
    patterns = check_keyboard_patterns(password)
    results['keyboard_patterns'] = patterns
    if patterns:
        steps.append(f"> [!] Keyboard patterns found: {', '.join(patterns)}")
    else:
        steps.append("> [*] No common keyboard patterns detected.")

    # 4. Leet speak dictionary check
    leet_matches = check_leet_dictionary(password, COMMON_WORDS)
    results['leet_matches'] = leet_matches
    if leet_matches:
        steps.append(f"> [!] Leet/dictionary matches: {', '.join(leet_matches)}")
    else:
        steps.append("> [*] No leet/dictionary matches detected.")

    # 5. Brute-force time estimate
    seconds = brute_force_time(password)
    results['brute_force_seconds'] = seconds
    results['brute_force_minutes'] = seconds / 60
    results['brute_force_hours'] = seconds / 3600
    results['brute_force_days'] = seconds / 86400
    results['brute_force_years'] = seconds / 31536000
    if seconds < 60:
        steps.append(f"> [!] Brute-force time: {seconds:.2f} seconds (Very Weak)")
    elif seconds < 3600:
        steps.append(f"> [!] Brute-force time: {seconds/60:.2f} minutes (Weak)")
    elif seconds < 86400:
        steps.append(f"> [*] Brute-force time: {seconds/3600:.2f} hours")
    elif seconds < 31536000:
        steps.append(f"> [*] Brute-force time: {seconds/86400:.2f} days")
    else:
        steps.append(f"> [*] Brute-force time: {seconds/31536000:.2f} years")

    # 6. Check Have I Been Pwned (HIBP) database
    hibp_count = -1
    try:
        hibp_count = pwnedpasswords.check(password)
        results['hibp_count'] = hibp_count
        if hibp_count > 0:
            steps.append(f"> [!] Found in {hibp_count} real-world breaches (HIBP).")
        else:
            steps.append("> [*] Not found in real-world breaches (HIBP).")
    except requests.exceptions.RequestException as e:
        results['error'] = (results['error'] + "; " if results['error'] else "") + f"Could not check HIBP: Network error ({e})"
        results['hibp_count'] = -1
        steps.append(f"> [!] Could not check HIBP: Network error.")
    except Exception as e:
        results['error'] = (results['error'] + "; " if results['error'] else "") + f"Error during HIBP check: {e}"
        results['hibp_count'] = -1
        steps.append(f"> [!] HIBP check error: {e}")

    # Custom dictionary check
    if custom_dict:
        matches = [w for w in custom_dict if w and w.lower() in password.lower()]
        results['custom_dict_matches'] = matches
        if matches:
            steps.append(f"> [!] Custom dictionary match: {', '.join(matches)}")
            results['extra_checks'].append(f"Password contains disallowed word(s): {', '.join(matches)}.")

    # 7. Deep checks (if requested)
    if deep:
        extra = results['extra_checks']
        # Check for repeated chars
        if len(set(password)) == 1:
            extra.append('Password is made of a single repeated character (very weak).')
            steps.append('> [!] Password is a single repeated character.')
        # Check for sequential patterns (e.g. abc, 123, qwerty...)
        seq = 'abcdefghijklmnopqrstuvwxyz'
        seq_num = '0123456789'
        pw_lower = password.lower()
        found_seq = any(s in pw_lower for s in [seq[i:i+3] for i in range(len(seq)-2)])
        found_seq_num = any(s in pw_lower for s in [seq_num[i:i+3] for i in range(len(seq_num)-2)])
        if found_seq or found_seq_num:
            extra.append('Password contains sequential letters or numbers (easily guessable).')
            steps.append('> [!] Sequential pattern detected.')
        # Check for common substitutions (e.g. p@ssw0rd)
        common_subs = {'@':'a','1':'i','!':'i','0':'o','$':'s','5':'s','3':'e','7':'t'}
        for k, v in common_subs.items():
            if k in password:
                steps.append(f'> [*] Found common substitution: {k}->{v}')
        # Check for date patterns (e.g. 1990, 2020)
        import re
        if re.search(r'(19|20)\d{2}', password):
            extra.append('Password contains a year (e.g. birth year, weak).')
            steps.append('> [!] Year pattern detected.')
        # Check for palindrome
        if len(password) > 3 and password == password[::-1]:
            extra.append('Password is a palindrome (weak).')
            steps.append('> [!] Password is a palindrome.')
        # Check for keyboard walks (e.g. qwerty, asdf)
        keyboard_walks = ['qwerty','asdf','zxcv','1234','qaz','wsx']
        if any(w in pw_lower for w in keyboard_walks):
            extra.append('Password contains keyboard walk patterns (very weak).')
            steps.append('> [!] Keyboard walk pattern detected.')
        # Check for common words fully present
        if pw_lower in COMMON_WORDS:
            extra.append('Password is a common word or password (very weak).')
            steps.append('> [!] Password is a common word.')
        # Check for short length
        if len(password) < 8:
            extra.append('Password is very short (less than 8 chars).')
            steps.append('> [!] Password is very short.')
        # Check for whitespace
        if ' ' in password:
            extra.append('Password contains whitespace.')
            steps.append('> [*] Password contains whitespace.')
        # Check for dictionary words inside password
        found_words = [w for w in COMMON_WORDS if w in pw_lower and len(w) > 3]
        if found_words:
            extra.append(f'Contains common word(s): {", ".join(found_words[:3])}...')
            steps.append(f'> [!] Contains common word(s): {", ".join(found_words[:3])}...')
        # Custom blacklist check (user-supplied)
        BLACKLIST = set(['password', 'letmein', '123456', 'admin', 'welcome', 'qwerty', 'passw0rd', 'iloveyou', 'monkey', 'dragon', 'sunshine', 'princess', 'football', 'baseball', 'abc123', 'trustno1'])
        if pw_lower in BLACKLIST:
            extra.append('Password is in a known blacklist (very weak).')
            steps.append('> [!] Password is in a known blacklist.')
        # Check for email/username patterns
        if re.search(r'^[\w\.-]+@[\w\.-]+\.[a-z]{2,}$', password):
            extra.append('Password looks like an email address (not recommended).')
            steps.append('> [!] Password looks like an email address.')
        if re.search(r'^[a-z0-9_\.-]{3,}$', password) and not re.search(r'[^a-z0-9_\.-]', password):
            extra.append('Password looks like a username (not recommended).')
            steps.append('> [!] Password looks like a username.')
        # Check for phone number patterns
        if re.search(r'\b\d{10,}\b', password):
            extra.append('Password contains a phone number pattern (not recommended).')
            steps.append('> [!] Password contains a phone number pattern.')
        # Check for credit card patterns (basic)
        if re.search(r'\b(?:\d[ -]*?){13,16}\b', password):
            extra.append('Password contains a credit card-like pattern (not recommended).')
            steps.append('> [!] Password contains a credit card-like pattern.')
    steps.append('> [*] Analysis complete.')
    return results