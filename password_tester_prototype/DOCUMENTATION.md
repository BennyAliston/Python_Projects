# Password Tester Web Application — Documentation

## Table of Contents
1. [Introduction](#introduction)
2. [System Overview](#system-overview)
3. [Architecture & Workflow](#architecture--workflow)
4. [Feature Details](#feature-details)
5. [How It Works: End-to-End Flow](#how-it-works-end-to-end-flow)
6. [Setup & Installation](#setup--installation)
7. [Usage Guide](#usage-guide)
8. [Custom Dictionary Upload](#custom-dictionary-upload)
9. [Security & Privacy](#security--privacy)
10. [Accessibility & Responsiveness](#accessibility--responsiveness)
11. [Deployment](#deployment)
12. [Troubleshooting](#troubleshooting)
13. [Contributing](#contributing)
14. [License](#license)

---

## 1. Introduction
The Password Tester is a Django-based web application that helps users analyze password strength, check for breaches, and generate strong passwords. It is designed for educational and ethical use, offering advanced feedback and security insights.

## 2. System Overview
- **Backend:** Python 3, Django 5.x
- **Frontend:** HTML5, CSS3, JavaScript (zxcvbn via CDN)
- **Database:** SQLite (default, can use PostgreSQL/MySQL)
- **External APIs:** HaveIBeenPwned for breach checks

## 3. Architecture & Workflow
- **MVC Pattern:**
  - **Models:** Store custom disallowed words/phrases (DisallowedWord).
  - **Views:** Handle password analysis, breach checks, and dictionary uploads.
  - **Templates:** Render UI, handle client-side logic, and provide accessibility.
- **Frontend:**
  - Uses zxcvbn.js (via CDN) for real-time strength estimation.
  - JavaScript for UI feedback, copy-to-clipboard, and breach checks.
- **Backend:**
  - Handles password submissions, dictionary uploads, and advanced analysis.
  - Stores custom dictionary words in the database.
- **Security:**
  - Passwords are never stored or logged.
  - Breach checks use k-anonymity (only a hash prefix is sent to the API).

## 4. Feature Details
### 4.1 Password Strength Meter
- Uses zxcvbn.js for advanced strength estimation (entropy, feedback, and score from 0–4).
- Visual strength bar updates in real time as you type.
- Policy checklist shows which requirements are met (length, uppercase, number, symbol).
- Entropy (bits) is displayed for technical users.

### 4.2 Password Breach Check
- Checks if the password has appeared in known data breaches using the HaveIBeenPwned API.
- Password is hashed with SHA-1 in the browser; only the first 5 chars of the hash are sent to the API (privacy-preserving).
- Shows a warning if the password is found in a breach, with actionable advice.

### 4.3 Password Generator
- Customizable generator lets users choose length (8–32), and include/exclude uppercase, lowercase, numbers, and symbols.
- Generates a random password meeting the selected criteria.
- Suggested password can be copied to clipboard.

### 4.4 Clipboard Copy Feedback
- All copy buttons trigger a floating “Copied!” toast notification for instant feedback.
- Works for both user-entered and generated passwords.

### 4.5 Custom Dictionary Upload
- Upload a `.txt` file with disallowed words/phrases (one per line).
- Words are stored in the database and checked against entered passwords.
- Helps enforce organization-specific password policies.

### 4.6 Accessibility & Responsiveness
- All interactive elements have ARIA labels.
- Keyboard navigation is fully supported.
- Responsive design ensures usability on desktop and mobile devices.

## 5. How It Works: End-to-End Flow
1. **User visits the app:** The main page loads with the password input, strength meter, and breach check ready.
2. **Password Entry:**
   - As the user types, zxcvbn.js analyzes the password and updates the strength meter, checklist, and entropy.
   - Simultaneously, the password is hashed and checked against HaveIBeenPwned for breaches.
   - Feedback and warnings are displayed in real time.
3. **Password Generator:**
   - User sets options and clicks “Suggest Password.”
   - A strong password is generated and placed in the compare field.
4. **Clipboard:**
   - User clicks “Copy,” and the password is copied with a toast notification.
5. **Custom Dictionary Upload:**
   - User uploads a `.txt` file; words are added to the DisallowedWord model in the database.
   - Passwords are checked against this list during analysis.
6. **Accessibility:**
   - All features are accessible by keyboard and screen reader.
7. **Mobile:**
   - Layout adapts for smaller screens with touch-friendly controls.

## 6. Setup & Installation
See the [README.md](README.md) for full instructions:
- Clone, create a virtualenv, install dependencies, migrate, run the server.

## 7. Usage Guide
- **Analyze Password:** Enter a password and click Analyze. View strength, entropy, and breach status.
- **Compare Passwords:** Use the compare field for side-by-side analysis.
- **Password Generator:** Customize options and generate a strong password.
- **Clipboard:** Copy any password with a single click ("Copied!" toast appears).
- **Custom Dictionary:** Upload a `.txt` file of disallowed words/phrases (one per line).

## 8. Custom Dictionary Upload
- Go to the “Upload Custom Disallowed Words/Phrases” section.
- Select a `.txt` file and click “Upload Dictionary.”
- Each word/phrase will be added to your database and checked against all future passwords.

## 9. Security & Privacy
- Passwords are never stored or logged.
- Breach checks use k-anonymity (only a hash prefix sent to the API).
- Custom dictionaries are stored in your database, not on disk.
- **Do not use real passwords in this demo.**

## 10. Accessibility & Responsiveness
- All interactive elements have ARIA labels.
- Keyboard navigation is supported.
- Responsive design for desktop and mobile.

## 11. Deployment
- Recommended free hosts: Render.com, Railway.app, Fly.io (see README for details).
- Steps: Push to GitHub, connect to host, deploy, set up custom domain.

## 12. Troubleshooting
- **Server won’t start:** Check dependencies and migrations.
- **Breach check fails:** API may be down or network issue.
- **Password not analyzed:** Ensure all required fields are filled.
- **Dictionary upload fails:** Check file format (plain text, one word/phrase per line).

## 13. Contributing
- Fork the repo, make changes, and submit a pull request.
- Open issues for bugs or feature requests.

## 14. License
- For educational and ethical use only. See LICENSE for details.

---

**Questions?** Open an issue or contact the maintainer.
