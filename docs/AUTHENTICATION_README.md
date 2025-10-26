# Authentication & User Tracking System

This document explains the authentication system for the admin dashboard and user name tracking for quiz attempts.

## Admin Authentication

### Overview
The admin dashboard and analytics endpoints are protected by simple username/password authentication using Flask sessions.

### Configuration

Set the following environment variables in your `.env` file:

```env
ADMIN_USERNAME=your_admin_username
ADMIN_PASSWORD=your_secure_password
```

**Default credentials (for development only):**
- Username: `admin`
- Password: `admin123`

⚠️ **Important:** Change these defaults before deploying to production!

### How It Works

1. **Login Page**: `/admin/login`
   - Users enter username and password
   - Credentials are verified against environment variables
   - On success, `admin_logged_in` flag is set in session
   - User is redirected to admin dashboard or original requested page

2. **Protected Routes**:
   - `/admin` - Admin dashboard (requires login)
   - `/api/analytics/*` - All analytics endpoints (requires login)
   
3. **Logout**: `/admin/logout`
   - Clears session data
   - Redirects to home page

### Usage

**Accessing the Admin Dashboard:**

1. Navigate to: `http://localhost:5000/admin`
2. If not logged in, you'll be redirected to `/admin/login`
3. Enter your credentials
4. You'll be redirected to the dashboard

**Direct Login:**
```
http://localhost:5000/admin/login
```

**Logout:**
```
http://localhost:5000/admin/logout
```

### Implementation Details

**Decorator Function** (`app.py`):
```python
def admin_required(f):
    """Decorator to require admin authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function
```

**Protected Route Example**:
```python
@app.route('/admin')
@admin_required
def admin_dashboard():
    return render_template('admin_dashboard.html')
```

**Analytics Protection** (`analytics.py`):
```python
def require_admin():
    """Decorator for analytics endpoints"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get('admin_logged_in'):
                return jsonify({'error': 'Authentication required'}), 401
            return f(*args, **kwargs)
        return decorated_function
    return decorator
```

## User Name Tracking

### Overview
Quiz attempts now track the name of the user who took the quiz. Names are stored locally in the browser and sent with quiz submissions.

### How It Works

1. **Name Input Modal**:
   - Appears before quiz starts (Elimination and Finals modes)
   - User enters their name
   - Name is saved to `localStorage` for future quizzes
   - Modal is dismissed and quiz begins

2. **LocalStorage**:
   - Key: `quizUserName`
   - Value: User's name (string)
   - Persists across browser sessions
   - Auto-fills on subsequent quizzes

3. **Submission**:
   - Name is sent as hidden field `user_name` with quiz answers
   - Stored in `QuizAttempt.user_name` column
   - Defaults to "Anonymous" if not provided

### Database Schema

**QuizAttempt Table** (models.py):
```python
class QuizAttempt(db.Model):
    # ... other fields ...
    user_name = db.Column(db.String(100))
```

### Implementation

**Frontend (JavaScript)**:
```javascript
// Check if name is already stored
const storedName = localStorage.getItem('quizUserName');
if (storedName) {
    userNameInput.value = storedName;
}

// Save name on submission
nameForm.addEventListener('submit', function(e) {
    e.preventDefault();
    const userName = userNameInput.value.trim();
    localStorage.setItem('quizUserName', userName);
    userNameHidden.value = userName;
    nameModal.classList.add('hidden');
    startTimer();
});
```

**Backend (Python)**:
```python
# Get user name from form
user_name = request.form.get('user_name', 'Anonymous')

# Create attempt with user name
attempt = QuizAttempt(
    session_id=session_id,
    quiz_mode='elimination_full',
    total_questions=total,
    correct_answers=correct,
    answers=results,
    user_name=user_name
)
```

### Affected Routes

The following submission routes now accept and store `user_name`:

1. **Elimination Mode**: `/elimination/submit` (POST)
2. **Finals Mode**: `/finals/submit` (POST)

**Note:** Review mode doesn't save attempts to database, so user names aren't stored for review quizzes.

### UI Components

**Name Modal Template** (in `elimination_mode.html`, `finals_mode.html`):
- Responsive design with Tailwind CSS
- Icon and welcoming message
- Auto-populated from localStorage
- Hidden form field for submission

### Sample Data

The `insert_sample_data.py` script generates quiz attempts with randomized user names from a predefined list:

```python
SAMPLE_NAMES = [
    'John Doe', 'Jane Smith', 'Mike Johnson', ...
]

attempt = QuizAttempt(
    # ... other fields ...
    user_name=random.choice(SAMPLE_NAMES)
)
```

### Analytics Integration

User names appear in:
- Recent attempts table in admin dashboard
- Analytics API responses (when user_name field is included)
- QuizAttempt.to_dict() method

### Clearing Stored Name

To clear the stored name from browser:

**JavaScript Console**:
```javascript
localStorage.removeItem('quizUserName');
```

**Or programmatically**:
```javascript
// Add a "clear name" button
document.getElementById('clearNameBtn').addEventListener('click', () => {
    localStorage.removeItem('quizUserName');
    alert('Name cleared!');
});
```

## Security Considerations

### Admin Authentication
- ✅ Session-based (secure when HTTPS is used)
- ✅ Environment variable configuration
- ✅ Redirect after login preserves intended destination
- ⚠️ No password hashing (simple auth for admin-only app)
- ⚠️ No rate limiting (add if needed)
- ⚠️ No multi-factor authentication

### User Names
- ✅ Client-side storage (localStorage)
- ✅ Optional field (defaults to "Anonymous")
- ✅ No authentication required (quiz takers don't need accounts)
- ⚠️ Trusts client-provided names (not verified)
- ⚠️ No profanity filtering

## Future Enhancements

Potential improvements:

1. **Admin System**:
   - Password hashing with bcrypt
   - Multiple admin accounts
   - Role-based permissions
   - Password reset functionality
   - Session timeout

2. **User Tracking**:
   - Email verification
   - User accounts with login
   - Quiz history per user
   - Leaderboards
   - Certificates/badges

## Testing

### Test Admin Login

1. Start the Flask app: `python app.py`
2. Navigate to: `http://localhost:5000/admin`
3. Enter credentials
4. Verify dashboard loads
5. Check analytics endpoints return data
6. Test logout functionality

### Test User Name Input

1. Navigate to: `http://localhost:5000/elimination`
2. Verify modal appears
3. Enter name and submit
4. Complete and submit quiz
5. Check database: `SELECT user_name FROM quiz_attempts ORDER BY created_at DESC LIMIT 1;`
6. Verify name is stored

### Test LocalStorage Persistence

1. Enter name in modal
2. Submit quiz
3. Start new quiz
4. Verify name auto-fills in modal

## Troubleshooting

**Admin Login Issues:**

```
Problem: "Invalid credentials" error
Solution: Check .env file has correct ADMIN_USERNAME and ADMIN_PASSWORD
```

```
Problem: Redirects to login after successful authentication
Solution: Check SECRET_KEY is set in .env and session cookies are enabled
```

**User Name Issues:**

```
Problem: Name modal doesn't appear
Solution: Check browser console for JavaScript errors
```

```
Problem: Name not saved in database
Solution: Verify models.py has user_name column and database migration was run
```

```
Problem: Name doesn't auto-fill
Solution: Check localStorage in browser DevTools (Application tab)
```

## API Reference

### Admin Login Endpoint

**POST** `/admin/login`

**Form Data:**
- `username` (string, required)
- `password` (string, required)

**Query Parameters:**
- `next` (string, optional) - URL to redirect after successful login

**Responses:**
- `302 Redirect` - Success, redirects to dashboard or `next` URL
- `200 OK` - Shows login page with error message

### Logout Endpoint

**GET** `/admin/logout`

**Responses:**
- `302 Redirect` - Redirects to home page

### Protected Analytics Endpoints

All `/api/analytics/*` endpoints require admin authentication:

**Unauthorized Response:**
```json
{
  "error": "Authentication required"
}
```
**HTTP Status:** `401 Unauthorized`

## Migration Guide

### Adding Authentication to Existing Installation

1. **Update Environment Variables**:
```bash
echo "ADMIN_USERNAME=your_username" >> .env
echo "ADMIN_PASSWORD=your_password" >> .env
```

2. **Update Database Schema**:
```bash
python
>>> from app import create_app
>>> from models import db
>>> app = create_app()
>>> with app.app_context():
...     db.engine.execute("ALTER TABLE quiz_attempts ADD COLUMN user_name VARCHAR(100)")
```

3. **Restart Application**:
```bash
python app.py
```

4. **Test Authentication**:
- Visit `/admin` and verify login required
- Test with credentials
- Verify dashboard loads

5. **Test User Names**:
- Take a quiz with name
- Check database for user_name value

---

**Last Updated:** December 2024  
**Version:** 1.0.0
