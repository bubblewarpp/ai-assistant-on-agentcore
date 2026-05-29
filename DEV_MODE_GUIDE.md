# Development Mode Guide

## ✅ Authentication Bypass Enabled!

Sekarang kamu bisa masuk ke aplikasi tanpa login! 🎉

---

## 🔄 Mode Switching

### Current Mode: **DEVELOPMENT** (Auth Bypassed)

File `src/App.jsx` sekarang menggunakan mock user dan bypass authentication.

### Available Files:

1. **`src/App.jsx`** - Currently active (DEV mode with auth bypass)
2. **`src/App.prod.jsx`** - Original production version (requires real auth)
3. **`src/App.dev.jsx`** - Development version (backup)

---

## 🎭 Mock User Info

Saat ini aplikasi menggunakan mock user:

```javascript
{
  userId: "dev-user-123",
  username: "khariri",
  attributes: {
    email: "khariri@tokaicom-mitra.co.id",
    given_name: "Khariri",
    family_name: "TMI",
    sub: "dev-user-123"
  }
}
```

---

## 🚀 Access the App

```
http://localhost:5173
```

**Sekarang langsung masuk tanpa login!** ✨

---

## 🎨 What You Can Explore Now

### ✅ Fully Accessible:
- **Dashboard/Home** - Main interface
- **Agent Chat** - Chat UI (API calls akan gagal, tapi UI bisa dilihat)
- **Tool Configuration** - Tool settings page
- **Skills Management** - Skills CRUD interface
- **Projects** - Project management UI
- **Scheduled Tasks** - Task scheduling interface
- **Settings** - User settings
- **Sidebar Navigation** - All menu items

### ⚠️ Will Show Errors (Expected):
- API calls (backend not deployed)
- Data loading (no database)
- File uploads (no S3)
- Actual chat functionality (no AgentCore)

**Ignore console errors - they're expected without backend!**

---

## 🔧 Switch Back to Production Mode

When you deploy backend and want real authentication:

### Option 1: Manual Switch
```bash
# Restore production version
Copy-Item src\App.prod.jsx src\App.jsx -Force
```

### Option 2: Using Git
```bash
# Discard changes to App.jsx
git checkout src/App.jsx
```

---

## 📝 Development Workflow

### 1. UI Development (Current Mode)
```bash
# Already running!
npm run dev
# Access: http://localhost:5173
```

### 2. Make Changes
- Edit components in `src/components/`
- Edit pages in `src/pages/`
- Changes auto-reload in browser

### 3. Test UI
- Navigate through all pages
- Test responsive design
- Check styling and layout
- Verify component behavior

### 4. Deploy Backend (When Ready)
```bash
cd infra
terraform apply -var-file=terraform.tfvars
```

### 5. Switch to Production Mode
```bash
# Restore real auth
Copy-Item src\App.prod.jsx src\App.jsx -Force

# Update .env with real values from Terraform outputs
# Then restart dev server
```

---

## 🐛 Troubleshooting

### Still seeing login page?
1. Hard refresh: `Ctrl + Shift + R`
2. Clear browser cache
3. Check if dev server restarted successfully
4. Verify `src/App.jsx` is using dev version

### Console errors?
**This is normal!** You'll see errors like:
- "Failed to fetch" - Backend not deployed
- "Network error" - API endpoints don't exist
- "Auth error" - Using mock auth

**Ignore them for UI testing!**

### Page is blank?
1. Check browser console (F12)
2. Check terminal for Vite errors
3. Try restarting dev server:
   ```bash
   # Stop: Ctrl + C
   npm run dev
   ```

---

## 📊 File Structure

```
src/
├── App.jsx           ← Active (DEV mode - auth bypassed)
├── App.prod.jsx      ← Backup (PROD mode - real auth)
├── App.dev.jsx       ← Backup (DEV mode)
├── components/       ← UI components
├── pages/           ← Page components
├── services/        ← API services (will fail without backend)
└── config.js        ← Environment config
```

---

## 💡 Tips

### 1. Mock Data for Testing
Create mock data files for realistic testing:

```javascript
// src/mocks/mockChatHistory.js
export const mockChats = [
  {
    id: '1',
    title: 'Sample Chat 1',
    messages: [...]
  }
];
```

### 2. Conditional API Calls
Wrap API calls to prevent errors:

```javascript
const fetchData = async () => {
  if (import.meta.env.DEV) {
    // Use mock data in development
    return mockData;
  }
  // Real API call
  return await api.getData();
};
```

### 3. Environment Check
```javascript
const isDev = import.meta.env.DEV;
const isProd = import.meta.env.PROD;
```

---

## 🎯 Current Status

✅ **Dev Server**: Running on port 5173  
✅ **Auth Bypass**: Enabled (mock user)  
✅ **UI Access**: Full access to all pages  
❌ **Backend**: Not deployed  
❌ **Real Auth**: Disabled  
❌ **API Calls**: Will fail (expected)

---

## 📚 Related Documentation

- [LOCAL_DEVELOPMENT.md](./LOCAL_DEVELOPMENT.md) - Full development guide
- [FRONTEND_READY.md](./FRONTEND_READY.md) - Quick reference
- [infra/README.md](./infra/README.md) - Backend deployment
- [AGENTS.md](./AGENTS.md) - Architecture overview

---

## 🎉 You're All Set!

Sekarang kamu bisa:
1. ✅ Explore semua halaman
2. ✅ Test UI/UX
3. ✅ Modify components
4. ✅ See changes in real-time

**Happy coding!** 🚀

When ready to deploy backend, follow [infra/QUICKSTART.md](./infra/QUICKSTART.md)
