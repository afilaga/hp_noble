# Agent 2: FRONTEND_OPS (React & Deployment)

**Focus**: UI Development, GitHub Workflow, Asset Management.
**Work Directory**: `Site/HookahPlaсe Noble Site/`

## 📋 Context / Memory
- **Repository**: `https://github.com/afilaga/hp_noble.git`
- **Deployment**: Automatic via GitHub Actions on `git push`.
- **API**: `https://api.hpnoble.ru/api` (once VPS SSL is ready).

## 🛠 Workflow & Commands

### 1. Local Development
   ```bash
   npm run dev
   ```

### 2. Updating Gallery
   Images are automatically detected in `src/assets/gallery/`.
   - Add new photos to `src/assets/gallery/`.
   - Delete old photos from the same folder.
   - Files are imported dynamically via `import.meta.glob`.

### 3. Deployment (Auto-deploy)
   Instead of manual SCP, just push to GitHub:
   ```bash
   git add .
   git commit -m "Description of changes"
   git push
   ```
   *The action builds the project and uploads it to `www/hpnoble.ru` on Reg.ru.*

## ⚠️ Operation Rules
- **Gallery**: Do not hardcode image paths in `Gallery.jsx`. Use the dynamic import system.
- **Environment**: Production API is set in `.github/workflows/deploy_frontend.yml`. For local testing, use `.env`.
- **Styles**: Mobile-first approach. Check `.section-title` and `.reservation-card` on mobile (max-width: 768px).

## 🔍 Verification
- Check deployment status: `GitHub -> Actions`.
- Verify live site: `https://hpnoble.ru`.
- Check browser console for "Mixed Content" or CORS errors.