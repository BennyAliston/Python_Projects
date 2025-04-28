from django.shortcuts import render
from .utils import check_password_strength
from django.utils.crypto import get_random_string
from django.core.files.uploadedfile import UploadedFile
from .models import DisallowedWord

# Create your views here.

PASSWORD_POLICY = [
    ("At least 8 characters", lambda pw: len(pw) >= 8),
    ("At least 1 uppercase letter", lambda pw: any(c.isupper() for c in pw)),
    ("At least 1 lowercase letter", lambda pw: any(c.islower() for c in pw)),
    ("At least 1 digit", lambda pw: any(c.isdigit() for c in pw)),
    ("At least 1 symbol", lambda pw: any(not c.isalnum() for c in pw)),
]


def index(request):
    context = {}
    # Handle custom dictionary deletion
    if request.method == 'POST' and request.POST.get('delete_custom_dict'):
        deleted_count = DisallowedWord.objects.all().delete()[0]
        context['custom_dict_status'] = f"Custom dictionary deleted. {deleted_count} entries removed."
    # Handle custom dictionary upload
    if request.method == 'POST' and 'custom_dict' in request.FILES:
        uploaded_file = request.FILES['custom_dict']
        if isinstance(uploaded_file, UploadedFile):
            try:
                words = uploaded_file.read().decode('utf-8').splitlines()
                words = [w.strip() for w in words if w.strip()]
                added = 0
                for w in words:
                    if not DisallowedWord.objects.filter(word__iexact=w).exists():
                        DisallowedWord.objects.create(word=w)
                        added += 1
                context['custom_dict_status'] = f"Custom dictionary uploaded. {added} new entries added."
            except Exception as e:
                context['custom_dict_status'] = f"Failed to upload dictionary: {e}"
    # Show custom dictionary status if present
    dict_count = DisallowedWord.objects.count()
    if dict_count > 0:
        context['custom_dict_status'] = f"Custom dictionary loaded with {dict_count} entries."
    if request.method == 'POST':
        password = request.POST.get('password', '')
        compare_pw = request.POST.get('compare_password', '')
        # Password history validator
        password_history = request.session.get('password_history', [])
        reused_password = password in password_history if password else False
        if password and password not in password_history:
            password_history.append(password)
            # Limit history size to last 10 passwords
            password_history = password_history[-10:]
            request.session['password_history'] = password_history
        context['reused_password'] = reused_password
        # Load custom dictionary for check
        custom_dict = list(DisallowedWord.objects.values_list('word', flat=True))
        if password:
            strength_results = check_password_strength(password, deep=True, custom_dict=custom_dict)
            context['results'] = strength_results
            context['password_checked'] = password
            context['hacker_steps'] = strength_results.get('steps', [])
            # Password policy check (basic feedback)
            policy_results = [(desc, rule(password)) for desc, rule in PASSWORD_POLICY]
            context['policy_results'] = policy_results
            # Split feedback
            basic_feedback = []
            advanced_feedback = []
            # Basic: length and char types
            for desc, ok in policy_results:
                if not ok:
                    basic_feedback.append(desc)
            # Advanced: entropy, breached, patterns
            if strength_results.get('entropy') is not None:
                advanced_feedback.append(f"Entropy: {strength_results['entropy']} bits")
            if strength_results.get('hibp_count') is not None:
                hibp = strength_results['hibp_count']
                if hibp > 0:
                    advanced_feedback.append(f"Found in {hibp} breaches!")
                elif hibp == 0:
                    advanced_feedback.append("Not found in breaches.")
            if strength_results.get('keyboard_patterns'):
                advanced_feedback.append(f"Keyboard patterns: {', '.join(strength_results['keyboard_patterns'])}")
            if strength_results.get('leet_matches'):
                advanced_feedback.append(f"Leet/dictionary matches: {', '.join(strength_results['leet_matches'])}")
            if strength_results.get('custom_dict_matches'):
                advanced_feedback.append(f"Custom dictionary matches: {', '.join(strength_results['custom_dict_matches'])}")
            if strength_results.get('extra_checks'):
                advanced_feedback.extend(strength_results['extra_checks'])
            context['basic_feedback'] = basic_feedback
            context['advanced_feedback'] = advanced_feedback
            # Comparison
            if compare_pw:
                compare_results = check_password_strength(compare_pw, deep=True, custom_dict=custom_dict)
                context['compare'] = {
                    'pw': compare_pw,
                    'results': compare_results
                }
        else:
            context['error'] = "Please enter a password."
        # Password generator
        if 'generate' in request.POST:
            gen_pw = get_random_string(14, allowed_chars='abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789!@#$%^&*()')
            context['generated_password'] = gen_pw
    else:
        context = {}
    return render(request, 'pwdchecker/index.html', context)