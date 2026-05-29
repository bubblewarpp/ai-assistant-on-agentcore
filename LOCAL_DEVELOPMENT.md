# Local Frontend Development Guide

## Quick Start (UI Testing Only)

Untuk melihat tampilan frontend tanpa deploy backend:

### 1. Install Dependencies

```bash
npm install
```

### 2. Run Development Server

```bash
npm run dev
```

Atau:

```bash
npm run start:local
```

### 3. Open Browser

```
http://localhost:5173
```

---

## ⚠️ Penting: Mode Development Lokal

File `.env.local` sudah dibuat dengan **mock values** untuk testing UI saja.

### ✅ Yang Bisa Dilakukan:
- ✅ Melihat tampilan UI/UX
- ✅ Test navigasi antar halaman
- ✅ Lihat layout dan styling
- ✅ Test responsive design
- ✅ Lihat komponen-komponen UI

### ❌ Yang TIDAK Bisa Dilakukan:
- ❌ Login/Authentication (Cognito belum ada)
- ❌ Chat dengan AI (Backend belum deploy)
- ❌ Simpan data (DynamoDB belum ada)
- ❌ Upload files (S3 belum ada)
- ❌ Semua API calls akan gagal

---

## Setelah Deploy Backend

Setelah menjalankan `terraform apply`, Anda perlu update environment variables dengan nilai yang sebenarnya.

### Option 1: Generate Otomatis (Recommended)

Jika ada script `generate-env.sh` atau dalam `deployment.sh`:

```bash
npm run generate-env
```

### Option 2: Manual

Buat file `.env` (bukan `.env.local`) dengan nilai dari Terraform outputs:

```bash
# Get outputs from Terraform
cd infra
terraform output
```

Kemudian buat `.env`:

```env
VITE_APP_SPARKY=<sparky_runtime_arn dari output>
VITE_COGNITO_DOMAIN=<cognito_domain dari output>
VITE_COGNITO_REGION=ap-southeast-1
VITE_USER_POOL_ID=<user_pool_id dari output>
VITE_APP_CLIENT_ID=<app_client_id dari output>
VITE_REDIRECT_SIGN_IN=<amplify_url dari output>
VITE_REDIRECT_SIGN_OUT=<amplify_url dari output>
VITE_SPARKY_MODEL_CONFIG=<model_config_json dari output>
```

---

## File Priority

Vite akan membaca environment variables dengan prioritas:

1. `.env.local` (highest priority - untuk development)
2. `.env.development` (untuk mode development)
3. `.env` (untuk semua modes)

**Tip:** Gunakan `.env.local` untuk testing UI, dan `.env` untuk development dengan backend yang sudah deploy.

---

## Available Scripts

```bash
# Development server (port 5173)
npm run dev

# Development server dengan mode development
npm run start:local

# Build untuk production
npm run build

# Preview production build
npm run preview

# Run tests
npm test

# Lint code
npm run lint

# Fix lint issues
npm run lint:fix

# Format code
npm run format
```

---

## Troubleshooting

### Port 5173 sudah digunakan

```bash
# Vite akan otomatis mencari port lain (5174, 5175, dst)
# Atau specify port manual:
npm run dev -- --port 3000
```

### Module not found errors

```bash
# Clear node_modules dan reinstall
rm -rf node_modules package-lock.json
npm install
```

### Hot reload tidak bekerja

```bash
# Restart dev server
# Ctrl+C untuk stop, kemudian npm run dev lagi
```

### Authentication errors di console

Ini normal jika menggunakan `.env.local` dengan mock values. Ignore saja atau:

```javascript
// Temporary: Comment out auth checks untuk UI testing
// Di src/App.jsx atau komponen auth
```

---

## Next Steps

1. **Test UI Lokal** - Pastikan tampilan sesuai keinginan
2. **Deploy Backend** - Jalankan `terraform apply`
3. **Update .env** - Ganti dengan nilai real dari Terraform
4. **Test Full Stack** - Login dan test semua fitur

---

## Tips Development

### 1. Mock Data untuk Testing

Buat file `src/mocks/mockData.js`:

```javascript
export const mockChatHistory = [
  {
    id: '1',
    role: 'user',
    content: 'Hello, how are you?',
    timestamp: new Date().toISOString()
  },
  {
    id: '2',
    role: 'assistant',
    content: 'I am doing well, thank you!',
    timestamp: new Date().toISOString()
  }
];
```

### 2. Disable Auth untuk UI Testing

Di `src/App.jsx`, temporary comment out auth:

```javascript
// Temporary for UI testing
const isAuthenticated = true; // Force authenticated state
```

### 3. Use React DevTools

Install React DevTools extension untuk Chrome/Firefox untuk debugging.

### 4. Check Console

Buka browser DevTools (F12) untuk melihat errors dan warnings.

---

## Production Build Testing

Sebelum deploy ke Amplify, test production build:

```bash
# Build
npm run build

# Preview
npm run preview
```

Buka `http://localhost:4173` untuk test production build.

---

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_APP_SPARKY` | Sparky AgentCore Runtime ARN | `arn:aws:bedrock-agentcore:...` |
| `VITE_COGNITO_DOMAIN` | Cognito domain name | `sparky-auth-domain-abc123` |
| `VITE_COGNITO_REGION` | AWS Region | `ap-southeast-1` |
| `VITE_USER_POOL_ID` | Cognito User Pool ID | `ap-southeast-1_ABC123` |
| `VITE_APP_CLIENT_ID` | Cognito App Client ID | `1234567890abcdef` |
| `VITE_REDIRECT_SIGN_IN` | OAuth redirect after login | `https://your-app.amplifyapp.com` |
| `VITE_REDIRECT_SIGN_OUT` | OAuth redirect after logout | `https://your-app.amplifyapp.com` |
| `VITE_SPARKY_MODEL_CONFIG` | JSON model configuration | `{"default_model_id":"..."}` |

---

## Need Help?

- Check browser console for errors
- Check terminal for Vite errors
- Review `src/config.js` for configuration
- Check `package.json` for available scripts
