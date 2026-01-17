# Agent 2: FRONTEND_OPS (React & Deployment)

**Focus**: UI Development, GitHub Workflow, Asset Management.
**Work Directory**: `Site/HookahPlaсe Noble Site/`

## 📋 Context / Memory
- **Repository**: `https://github.com/afilaga/hp_noble.git`
- **Deployment**: Automatic via GitHub Actions on `git push`.
- **API**: `https://whooks.filatiev.pro/webhook/` (n8n Automation).

## 🛠 Workflow & Commands

### 4. Form Validation
   - The reservation form uses active validation. The "Book" button is always clickable (except when `loading`).
   - Errors are displayed dynamically if fields are missing or the consent checkbox is unchecked.

## ⚠️ Operation Rules
- **Validation**: Do not use `disabled` attribute for form submission based on field state. Handle validation inside `submitReservation` to provide feedback to the user.
- **Gallery**: Do not hardcode image paths in `Gallery.jsx`. Use the dynamic import system.

- **Environment**: Production API is set in `.github/workflows/deploy_frontend.yml`. For local testing, use `.env`.
- **Styles**: Mobile-first approach. Check `.section-title` and `.reservation-card` on mobile (max-width: 768px).

## 🔍 Verification

- Check deployment status: `GitHub -> Actions`.

- Verify live site: `https://hpnoble.ru`.

- Check browser console for "Mixed Content" or CORS errors.

- **SEO Check**: Verify OG image at `https://hpnoble.ru/og-image.jpg` and check Meta Tags.



## 📈 SEO & Meta Management

- **OpenGraph**: Image is stored at `public/og-image.jpg`. To change the preview image, replace this file (keep the same name).

- **Keywords**: Main keywords ("кальянная в Сочи", "Воровского", "паровые коктейли") are located in `index.html`.

- **Structured Data**: JSON-LD schema in `index.html` links the site to the Telegram bot `@hp_noble_bot` for better indexing.
