# 🛠️ Admin Panel Setup Guide

## Quick Start: 3 Ways to Create an Admin User

### ⚡ **Method 1: Python Script (Recommended)**

```bash
cd backend
python3 create_admin.py
```

Follow the prompts:
- Option 1: Make existing user admin (if you already have an account)
- Option 2: Create new admin user

**Example:**
```
Choose an option:
  1. Make an existing user admin
  2. Create a new admin user

Enter choice (1 or 2): 2

Username: admin
Email: admin@billings.com
Password: SecurePassword123

✅ Admin user created successfully!
   Username: admin
   Email: admin@billings.com
   Password: SecurePassword123

🔐 Login at: http://localhost:8080/login.html
```

---

### 🗃️ **Method 2: Direct SQL**

**Option A: Make existing user admin**
```sql
-- 1. Find your user ID
SELECT id, username, email, is_admin FROM users;

-- 2. Make user admin (replace 1 with your user ID)
UPDATE users SET is_admin = TRUE WHERE id = 1;
```

**Option B: Create new admin user**
```sql
-- Run the SQL script
psql your_database_name < backend/create_admin.sql

-- This creates:
--   Username: admin
--   Email: admin@billings.com
--   Password: admin123
```

---

### 🔧 **Method 3: Using Database GUI**

If using pgAdmin, DBeaver, or similar:

1. Connect to your database
2. Find the `users` table
3. Locate your user row
4. Set `is_admin` column to `true`
5. Save

---

## 🚀 Access the Admin Panel

### 1. **Login**
- Go to: `http://localhost:8080/login.html`
- Use your admin credentials

### 2. **Navigate to Admin Panel**
- After login, go to: `http://localhost:8080/admin.html`
- OR click "Admin" in the navigation (if you add it)

### 3. **You'll See:**
```
┌─────────────────────────────────────┐
│ 🛠️ Admin Dashboard [ADMIN: username]│
│                                     │
│ [+ Add Question] [+ Create Achievement] [🔄 Refresh]│
│                                     │
│ ┌──────┐  ┌──────┐  ┌──────┐      │
│ │ 📝   │  │ 👥   │  │ 🏆   │      │
│ │Questions│ │Users │  │Achievements│  │
│ └──────┘  └──────┘  └──────┘      │
└─────────────────────────────────────┘
```

---

## 📋 Admin Panel Features

### **Admin Dashboard** (`/admin.html`)
- Platform overview statistics
- Quick access to all admin functions
- Recent activity feed (coming soon)

### **Question Management** (`/admin-questions.html`)
- ✅ Create new questions
- ✅ Edit existing questions
- ✅ Delete questions
- ✅ Search & filter
- ✅ Pagination (20 per page)
- ✅ Support for all 4 exam types

### **Achievement Management** (`/admin-achievements.html`)
- ✅ Create achievements
- ✅ Edit achievement criteria
- ✅ Delete achievements
- ✅ Set rarity levels
- ✅ Configure unlock conditions
- ✅ Assign XP rewards

---

## 🔐 Security Notes

### **Admin-Only Protection**
- All admin pages check `is_admin` field
- Non-admin users are automatically redirected
- JWT token validated on every API call
- 403 Forbidden returned for non-admin API access

### **API Endpoints (Admin Only)**
```
GET    /api/v1/admin/questions
POST   /api/v1/admin/questions
GET    /api/v1/admin/questions/{id}
PUT    /api/v1/admin/questions/{id}
DELETE /api/v1/admin/questions/{id}

GET    /api/v1/admin/achievements
POST   /api/v1/admin/achievements
PUT    /api/v1/admin/achievements/{id}
DELETE /api/v1/admin/achievements/{id}

GET    /api/v1/admin/users
GET    /api/v1/admin/users/{id}
```

---

## 🐛 Troubleshooting

### **"Access Denied" Message**
- Check `is_admin` field in database
- Make sure you're logged in with admin account
- Clear browser cache and re-login

### **"Failed to load" errors**
- Ensure backend is running: `uvicorn app.main:app --reload`
- Check browser console for errors (F12)
- Verify API endpoint URLs in `js/config.js`

### **Can't see admin navigation**
- Admin panel is separate from user dashboard
- Manually navigate to: `http://localhost:8080/admin.html`
- Bookmark it for quick access

---

## 🎯 Next Steps

After setting up admin access:

1. **Add some questions** - Build your question bank
2. **Create achievements** - Define unlock criteria
3. **Test the system** - Create a test user and try taking quizzes
4. **Customize** - Add more exam types or domains as needed

---

## 📞 Need Help?

**Common Issues:**

1. **No users in database**
   - Sign up at `/signup.html` first
   - Then make that user admin

2. **Migration not applied**
   ```bash
   cd backend
   alembic upgrade head
   ```

3. **Database connection error**
   - Check `.env` file has correct `DATABASE_URL`
   - Verify PostgreSQL is running

---

**Happy Admin-ing! 🎉**
