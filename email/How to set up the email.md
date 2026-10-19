# VentCourse sign-in email — setup

## 1. Upload the logo (once)
Upload `assets/logo/final/email-logo-240.png` to your GitHub repo **Venti-course-app** at `assets/logo/email-logo-240.png` (branch `main`).
The email loads it from:
https://raw.githubusercontent.com/manjukedarnath-svg/Venti-course-app/main/assets/logo/email-logo-240.png

## 2. EmailJS → Email Templates → your template
- **Subject:** `{{passcode}} is your VentCourse sign-in code`
- **To email:** `{{to_email}}`
- **From name:** `{{from_name}}`
- **Reply to:** `{{reply_to}}`
- **Content:** click **Edit content → Code editor**, paste everything from `OTP email - EmailJS template.html`, then Save.

Keep the variable names exactly: `{{passcode}}`, `{{time}}`, `{{username}}` (the app sends these).

## 3. Gmail profile picture
Gmail → Settings → Profile picture → upload `assets/logo/final/profile-gmail-800.png`. This shows next to the sender name in inboxes.

## Logo files (assets/logo/final)
- ventcourse-logo-transparent.png — transparent background, for slides/docs
- ventcourse-icon-1024 / 512 / 192.png — app icons
- apple-touch-icon-180.png — iPhone home screen
- favicon-32.png — browser tab
- email-logo-240.png — email header
- profile-gmail-800.png — Gmail profile picture
