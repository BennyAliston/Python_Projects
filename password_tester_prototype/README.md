# Password Tester

A simple web app to check password strength, analyze security, and generate strong passwords. Built with Django and JavaScript.

## Features
- Password strength meter (using zxcvbn)
- Checks if your password has appeared in data breaches (HaveIBeenPwned API)
- Strong password generator with options
- Copy passwords to clipboard
- Upload a custom dictionary of disallowed words/phrases

## Quick Start
1. Clone this repo
2. Create a virtual environment and activate it
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run migrations:
   ```bash
   python manage.py migrate
   ```
5. Start the server:
   ```bash
   python manage.py runserver
   ```
6. Open your browser at http://127.0.0.1:8000/

## Usage
- Enter a password to analyze its strength and check for breaches.
- Use the generator for a strong password suggestion.
- Upload a .txt file to add custom disallowed words.
- Use the delete button to clear the custom dictionary.

## Requirements
See `requirements.txt` for Python dependencies.

## Author
Kritagya Kumar (Benny Aliston)

## License
For educational/ethical use only. Do not use real passwords.
