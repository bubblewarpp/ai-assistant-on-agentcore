# Theme Customization Guide

## 🎨 Current Theme: Tokichan Gradient

Aplikasi sekarang menggunakan **animated gradient background** yang lebih unik dan tidak mirip Gemini!

---

## ✨ Features

### Light Mode:
- **Soft gradient** dari biru muda ke ungu muda
- **Animated mesh overlay** untuk depth
- **Smooth transitions** antar warna
- **Subtle animation** yang tidak mengganggu

### Dark Mode:
- **Deep gradient** dengan tone gelap
- **Muted overlay** untuk dark theme
- **Consistent animation** dengan light mode
- **Eye-friendly** untuk penggunaan malam

---

## 🎭 Gradient Colors

### Light Mode Gradient:
```css
From: hsl(220, 100%, 98%)  /* Soft blue */
Via:  hsl(260, 100%, 97%)  /* Soft purple */
To:   hsl(200, 100%, 98%)  /* Soft cyan */
```

### Dark Mode Gradient:
```css
From: hsl(240, 20%, 8%)    /* Deep blue-black */
Via:  hsl(260, 25%, 10%)   /* Deep purple-black */
To:   hsl(220, 20%, 9%)    /* Deep blue-black */
```

---

## 🔧 Customization Options

### Option 1: Change Gradient Colors

Edit `src/globals.css`:

```css
:root {
  /* Light mode - Customize these! */
  --gradient-from: 220 100% 98%;  /* Start color */
  --gradient-via: 260 100% 97%;   /* Middle color */
  --gradient-to: 200 100% 98%;    /* End color */
}

.dark {
  /* Dark mode - Customize these! */
  --gradient-from: 240 20% 8%;
  --gradient-via: 260 25% 10%;
  --gradient-to: 220 20% 9%;
}
```

### Option 2: Adjust Animation Speed

```css
html::before {
  animation: gradientShift 15s ease infinite;  /* Change 15s */
}

html::after {
  animation: meshMove 20s ease-in-out infinite;  /* Change 20s */
}
```

### Option 3: Change Gradient Direction

```css
html::before {
  background: linear-gradient(
    135deg,  /* Change angle: 0deg, 45deg, 90deg, 180deg, etc */
    hsl(var(--gradient-from)) 0%,
    hsl(var(--gradient-via)) 50%,
    hsl(var(--gradient-to)) 100%
  );
}
```

---

## 🎨 Pre-made Color Schemes

### 1. Ocean Breeze (Current)
```css
:root {
  --gradient-from: 220 100% 98%;  /* Blue */
  --gradient-via: 260 100% 97%;   /* Purple */
  --gradient-to: 200 100% 98%;    /* Cyan */
}
```

### 2. Sunset Glow
```css
:root {
  --gradient-from: 30 100% 98%;   /* Orange */
  --gradient-via: 350 100% 97%;   /* Pink */
  --gradient-to: 280 100% 98%;    /* Purple */
}
```

### 3. Forest Mist
```css
:root {
  --gradient-from: 140 60% 98%;   /* Green */
  --gradient-via: 180 60% 97%;    /* Teal */
  --gradient-to: 200 60% 98%;     /* Blue */
}
```

### 4. Lavender Dream
```css
:root {
  --gradient-from: 280 100% 98%;  /* Purple */
  --gradient-via: 300 100% 97%;   /* Magenta */
  --gradient-to: 260 100% 98%;    /* Violet */
}
```

### 5. Minimal Gray (No gradient)
```css
:root {
  --gradient-from: 0 0% 98%;      /* Light gray */
  --gradient-via: 0 0% 97%;       /* Lighter gray */
  --gradient-to: 0 0% 98%;        /* Light gray */
}
```

---

## 🚀 Advanced Customization

### Add More Gradient Stops

```css
html::before {
  background: linear-gradient(
    135deg,
    hsl(220, 100%, 98%) 0%,
    hsl(240, 100%, 97%) 25%,
    hsl(260, 100%, 97%) 50%,
    hsl(280, 100%, 97%) 75%,
    hsl(200, 100%, 98%) 100%
  );
}
```

### Radial Gradient Instead

```css
html::before {
  background: radial-gradient(
    circle at 50% 50%,
    hsl(var(--gradient-from)) 0%,
    hsl(var(--gradient-via)) 50%,
    hsl(var(--gradient-to)) 100%
  );
}
```

### Disable Animation

```css
html::before {
  animation: none;  /* Remove animation */
  background-position: 0% 50%;  /* Static position */
}

html::after {
  animation: none;
}
```

### Stronger Mesh Overlay

```css
html::after {
  background-image: 
    radial-gradient(at 20% 30%, hsla(260, 100%, 95%, 0.5) 0px, transparent 50%),
    radial-gradient(at 80% 70%, hsla(220, 100%, 95%, 0.5) 0px, transparent 50%),
    radial-gradient(at 50% 50%, hsla(240, 100%, 96%, 0.4) 0px, transparent 50%);
}
```

---

## 🎯 Quick Theme Switcher

Create different theme files:

### 1. Create `src/themes/ocean.css`
```css
:root {
  --gradient-from: 220 100% 98%;
  --gradient-via: 260 100% 97%;
  --gradient-to: 200 100% 98%;
}
```

### 2. Create `src/themes/sunset.css`
```css
:root {
  --gradient-from: 30 100% 98%;
  --gradient-via: 350 100% 97%;
  --gradient-to: 280 100% 98%;
}
```

### 3. Import in `src/main.jsx` or `src/index.jsx`
```javascript
// Switch between themes
import './themes/ocean.css';  // or './themes/sunset.css'
```

---

## 🔍 Troubleshooting

### Gradient not showing?
1. Check browser DevTools (F12)
2. Verify `html::before` and `html::after` are present
3. Check z-index is `-1`
4. Ensure no other background is overriding

### Animation too fast/slow?
Adjust the duration in `animation` property:
```css
animation: gradientShift 30s ease infinite;  /* Slower */
animation: gradientShift 5s ease infinite;   /* Faster */
```

### Want solid color instead?
Remove the gradient and use solid background:
```css
html {
  background: hsl(220, 100%, 98%);  /* Solid color */
}

html::before,
html::after {
  display: none;  /* Hide gradients */
}
```

---

## 💡 Design Tips

### 1. Keep it Subtle
- Use high lightness values (95-98%) for light mode
- Use low lightness values (8-12%) for dark mode
- Avoid high saturation (>50%) for backgrounds

### 2. Maintain Contrast
- Ensure text is readable on gradient
- Test with both light and dark text
- Use browser DevTools to check contrast ratio

### 3. Performance
- Gradients are GPU-accelerated
- Animations are smooth on modern browsers
- Consider disabling on low-end devices

### 4. Accessibility
- Provide option to disable animations
- Respect `prefers-reduced-motion`
- Maintain WCAG contrast ratios

---

## 📚 Color Theory

### HSL Format: `hsl(hue, saturation%, lightness%)`

- **Hue**: 0-360 (color wheel)
  - 0/360: Red
  - 60: Yellow
  - 120: Green
  - 180: Cyan
  - 240: Blue
  - 300: Magenta

- **Saturation**: 0-100%
  - 0%: Gray
  - 100%: Full color

- **Lightness**: 0-100%
  - 0%: Black
  - 50%: Pure color
  - 100%: White

### For Backgrounds:
- Light mode: 95-98% lightness
- Dark mode: 8-12% lightness
- Subtle: 20-40% saturation
- Vibrant: 80-100% saturation

---

## 🎨 Inspiration

Current design inspired by:
- Modern SaaS applications
- Glassmorphism trend
- Subtle depth and layering
- Smooth, calming animations

**Not inspired by:**
- ❌ Gemini (too purple/blue gradient)
- ❌ ChatGPT (too plain white)
- ❌ Claude (too minimal)

**Unique features:**
- ✅ Animated mesh overlay
- ✅ Multi-layer gradients
- ✅ Smooth color transitions
- ✅ Custom color scheme

---

## 🚀 Next Steps

1. **Test the current theme** - See if you like it
2. **Try different colors** - Use pre-made schemes above
3. **Adjust animation** - Speed up or slow down
4. **Create your own** - Mix and match colors
5. **Share feedback** - Let me know what you think!

---

**Enjoy your new gradient theme!** 🎨✨
