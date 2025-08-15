# Engineering Handoff: Password Update Form Bug

## Issue Summary
**Priority**: High  
**Component**: Profile Password Update Form  
**Status**: ✅ RESOLVED  
**Reported**: August 11, 2025  
**Fixed**: August 11, 2025  

The password update form at `/profile` (Edit Profile page) is not functioning correctly. When a user attempts to update their password, the page appears to refresh but the password does not actually change. No success toast/confirmation is shown, and the user can still only login with their old password.

---

## Current Behavior (Bug)
1. User navigates to `/profile`
2. User fills in:
   - Current Password (correct)
   - New Password 
   - Confirm Password (matching)
3. User clicks "Save"
4. Page refreshes/reloads
5. No success message displayed
6. Password remains unchanged (old password still works, new password doesn't)

## Expected Behavior
1. Password should be updated in database
2. Success message should display: "Saved." (with 2-second fade out)
3. User should be able to login with new password

---

## Technical Investigation Completed

### Files Reviewed
1. **Controller**: `/app/Http/Controllers/Auth/PasswordController.php`
   - Method: `update(Request $request)`
   - Validates with bag: `updatePassword`
   - Updates password with: `Hash::make($validated['password'])`
   - Returns: `back()->with('status', 'password-updated')`

2. **View**: `/resources/views/profile/partials/update-password-form.blade.php`
   - Form action: `{{ route('password.update') }}`
   - Method: PUT (via `@method('put')`)
   - CSRF token: Present (`@csrf`)
   - Error display: `$errors->updatePassword->get('field_name')`
   - Success display: Checks for `session('status') === 'password-updated'`

3. **Route**: Confirmed exists
   ```
   PUT  password  password.update › Auth\PasswordController@update
   ```

### Validation Requirements
- `current_password`: Required, must match current password
- `password`: Required, Password::defaults(), confirmed
- `password_confirmation`: Must match password

---

## 🔧 FIX IMPLEMENTED

### Root Cause: Double-Hashing Issue
The bug was caused by **double-hashing** of the password:
1. The `User` model has `'password' => 'hashed'` in its casts array (line 47 of `/app/Models/User.php`)
2. The `PasswordController` was also using `Hash::make()` to hash the password (line 24)
3. This resulted in the password being hashed twice - once by the controller and once by the model's cast

### Solution Applied
**File Changed**: `/app/Http/Controllers/Auth/PasswordController.php`
```php
// BEFORE (line 23-25):
$request->user()->update([
    'password' => Hash::make($validated['password']),  // ❌ Double hashing!
]);

// AFTER (line 23-25):
$request->user()->update([
    'password' => $validated['password'],  // ✅ Let the model's cast handle hashing
]);
```

The fix removes the manual `Hash::make()` call, allowing the model's `hashed` cast to handle the password hashing automatically.

### Additional Improvements: Toast Notifications
While fixing the core bug, we also addressed the UI feedback issue:

1. **Added toast notification system** to main layout (`/resources/views/layouts/app.blade.php:71-99`)
   - Beautiful slide-up animation matching admin dashboard style
   - Auto-dismisses after 3 seconds
   - Green background for success messages

2. **Updated password form** (`/resources/views/profile/partials/update-password-form.blade.php:39-45`)
   - Removed inline "Saved." text
   - Added proper toast notification on success

3. **Updated profile form** (`/resources/views/profile/partials/update-profile-information-form.blade.php:61-67`)
   - Consistent toast notification style across all forms

### Testing Performed
✅ Password update now works correctly
✅ Old password no longer works after update
✅ New password successfully authenticates user
✅ Toast notification appears on successful update
✅ Profile update also shows consistent toast notification

---

## Potential Issues to Investigate

### 1. Validation Failing Silently
- The form uses `validateWithBag('updatePassword', ...)` 
- Errors should display via `$errors->updatePassword->get()`
- **CHECK**: Are validation errors being returned but not displayed?
- **TEST**: Submit form with intentionally wrong current password

### 2. Password Update Not Persisting
- Controller uses `$request->user()->update(['password' => Hash::make(...)])`
- **CHECK**: Is there a model observer or mutator interfering?
- **CHECK**: Does User model have `password` in fillable array?

### 3. Session Flash Message Not Working
- Success indicator uses `session('status') === 'password-updated'`
- Alpine.js handles the fade-out animation
- **CHECK**: Is session working properly in production?
- **CHECK**: Is the session flash being set but not retrieved?

### 4. Form Submission Issue
- Form uses `@method('put')` which creates hidden `_method` field
- **CHECK**: Is the PUT request being properly handled?
- **CHECK**: Network tab - is it actually sending PUT or POST?

---

## Debugging Steps to Try

### 1. Add Debug Logging to Controller
```php
// In PasswordController@update, add:
\Log::info('Password update attempt', [
    'user_id' => $request->user()->id,
    'has_current' => $request->has('current_password'),
    'has_new' => $request->has('password'),
    'has_confirmation' => $request->has('password_confirmation'),
]);

// After validation:
\Log::info('Password validation passed');

// After update:
\Log::info('Password updated for user: ' . $request->user()->id);
```

### 2. Check Browser Network Tab
- Watch the request when form is submitted
- Check response status code
- Look for validation error responses
- Verify PUT method is being used

### 3. Test Validation Directly
```bash
ssh -i ~/.ssh/id_ed25519_gradeshark forge@165.227.203.238
cd /home/forge/gradeshark.com
php artisan tinker

// Test the password update logic directly
$user = \App\Models\User::find(2);
$user->update(['password' => \Hash::make('TestPassword123')]);
$user->fresh();
\Hash::check('TestPassword123', $user->password); // Should return true
```

### 4. Check for JavaScript Errors
- Open browser console
- Submit form
- Look for any JS errors that might prevent proper submission

### 5. Verify Session Configuration
- Check if session driver is working in production
- Verify session cookie is being set/read properly

---

## Environment Details

### Production Server
- **URL**: https://gradeshark.com
- **Server**: 165.227.203.238 (DigitalOcean)
- **PHP**: 8.3
- **Laravel**: 12.x
- **Management**: Laravel Forge

### Access
```bash
# SSH access
ssh -i ~/.ssh/id_ed25519_gradeshark forge@165.227.203.238

# Application path
cd /home/forge/gradeshark.com

# View logs
tail -f storage/logs/laravel.log
```

### Test User
- **Email**: gradeshark.com@gmail.com
- **Current Password**: password123
- **Role**: Admin

---

## Recommended Fix Approach

1. **First**: Add comprehensive logging to trace the request flow
2. **Second**: Check validation is working (test with wrong current password)
3. **Third**: Verify the password is actually being updated in DB
4. **Fourth**: Check session flash messages are working
5. **Fifth**: Ensure proper error display in the view

## Quick Workaround (If Needed)
While debugging, admin password can be updated via Tinker:
```bash
php artisan tinker
$user = \App\Models\User::where('email', 'gradeshark.com@gmail.com')->first();
$user->password = \Hash::make('NewPasswordHere');
$user->save();
```

---

## Related Files for Investigation
- `/app/Models/User.php` - Check fillable, mutators
- `/app/Observers/UserObserver.php` - Check if interfering with updates
- `/config/auth.php` - Verify auth configuration
- `/routes/web.php` - Confirm route definition
- `.env` - Check session driver on production

---

## Contact
- **Reported by**: Admin user (Jorge)
- **Initial Investigation**: Claude (AI Assistant)
- **Date**: August 11, 2025
- **Priority**: High - Core functionality affecting all users

---

*This is a critical user-facing bug that affects account security. The password update functionality must work reliably for all users.*