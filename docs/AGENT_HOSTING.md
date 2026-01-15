# Agent 2: HOSTING_OPS (Frontend & Database)

**Focus**: Reg.ru Hosting `31.31.197.32`, React, MySQL Admin, FTP.
**Work Directory**: `Site/HookahPlaсe Noble Site/`

## 📋 Context / Memory
- **Role**: Frontend Dev & Webmaster.
- **Key Files**:
    - `src/App.jsx` (UI)
    - `package.json` (Deps)
    - `.env` (`VITE_API_BASE`)

## 🛠 Primary Commands
### 1. Build for Prod
   ```bash
   npm run build
   ```

### 2. Upload (Deploy)
   *Use FTP or SCP to upload `dist/*` to `www/hpnoble.ru`.*
   ```bash
   scp -r dist/* u3370970@31.31.197.32:www/hpnoble.ru/
   ```

### 3. MySQL Config
   *Manage `u3370970_default` via phpMyAdmin on Reg.ru or SQL client.*

## ⚠️ Operation Rules
- **Sync**: Ensure local `.env` points to the correct production API (`http://178.20.211.174:8000/api` or domain).
- **Check**: Verify the build works locally with `npm run preview` before uploading.
