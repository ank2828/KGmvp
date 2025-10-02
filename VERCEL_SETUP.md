# Vercel Deployment Setup

## Required Settings in Vercel Dashboard

1. Go to your project settings: https://vercel.com/[your-project]/settings
2. Navigate to **General** → **Build & Development Settings**
3. Set the following:

### Root Directory
```
frontend
```
**Important:** Click "Edit" next to Root Directory and set it to `frontend`

### Build Command
```
npm run build
```

### Output Directory
```
.next
```

### Install Command
```
npm install
```

## That's it!

Once you set the Root Directory to `frontend`, Vercel will:
- Run `npm install` in the frontend folder
- Run `npm run build` which uses Turbopack
- Deploy the `.next` output directory

The app uses:
- ✅ Next.js 15 with App Router
- ✅ Tailwind CSS v4 (correct configuration)
- ✅ React Query for state management
- ✅ TypeScript

## Environment Variables

Don't forget to set in Vercel:
```
NEXT_PUBLIC_API_URL=https://your-backend-url.com
```
