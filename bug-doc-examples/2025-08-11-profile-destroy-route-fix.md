# Resolved: Missing profile.destroy Route & Account Deletion Policy

## Issue Summary
**Date Identified**: August 11, 2025  
**Date Resolved**: August 11, 2025  
**Type**: Configuration/Policy Decision  
**Affected Areas**: User profile page, account deletion functionality

## Discovery Context

### Initial Error
```
Symfony\Component\Routing\Exception\RouteNotFoundException
Route [profile.destroy] not defined.
```

### Investigation Findings
1. The `profile.destroy` route was missing from `routes/web.php`
2. The ProfileController had the `destroy()` method implemented
3. The view template referenced the route in `delete-user-form.blade.php`
4. Initial assumption: This was a bug from the Laravel Breeze scaffolding

### The Real Story
**Administrative Decision**: Prior to forking from MedComic, account self-deletion was intentionally disabled. This is standard practice for LMS platforms where user data has financial and educational implications.

## Original Implementation (Pre-Fork)

### Why Self-Deletion Was Removed
1. **Payment History**: User transactions must be preserved for accounting
2. **Course Progress**: Educational records need to be maintained
3. **Compliance**: Audit trails required for educational platforms
4. **Data Integrity**: Preventing accidental loss of student records
5. **Business Logic**: Only administrators should manage account lifecycle

## Current Solution

### Three-Layer Protection Implemented

#### 1. Route Level (routes/web.php)
```php
Route::delete('/profile', [ProfileController::class, 'destroy'])->name('profile.destroy');
```
- Route EXISTS to prevent 404 errors
- Maintains compatibility with Laravel Breeze structure
- Available for future admin-initiated deletion features

#### 2. View Level (profile/edit.blade.php)
```blade
{{-- Delete Account Section --}}
{{-- Disabled: Account deletion is admin-only for now --}}
@if(false)
    <div class="bg-theme-elevated border border-theme rounded-lg p-6 sm:p-8">
        <div class="max-w-xl">
            @include('profile.partials.delete-user-form')
        </div>
    </div>
@endif
```
- UI completely hidden from all users
- Easy to re-enable by changing condition
- Comment explains the policy decision

#### 3. Controller Level (ProfileController.php)
```php
public function destroy(Request $request): RedirectResponse
{
    // Account deletion is admin-only for now
    // Users cannot delete their own accounts
    abort(403, 'Account deletion must be performed by an administrator.');
    
    /* Original code preserved for when/if self-deletion is re-enabled:
    [original implementation preserved in comments]
    */
}
```
- Returns 403 Forbidden if accessed directly
- Original code preserved for future use
- Clear error message explaining the restriction

## Admin Deletion Capability

### Current State
- Admins CAN delete users through `/admin/users` interface
- Delete button available in user management table
- Proper confirmation required before deletion
- Admin's own account protected from self-deletion

### Protection for Admin Accounts
The profile edit view already had protection:
```blade
@if(!auth()->user()->isAdmin())
    {{-- Show delete section --}}
@endif
```
This prevented admins from accidentally deleting their own accounts.

## Policy Documentation

### Account Deletion Policy (as of August 2025)
1. **User Self-Deletion**: DISABLED
2. **Admin Deletion of Users**: ENABLED through admin panel
3. **Admin Self-Deletion**: DISABLED (prevents lockout)
4. **Future Consideration**: May implement "Request Deletion" workflow

### Rationale
- **Data Retention**: Educational records must be preserved
- **Financial Records**: Payment history required for accounting
- **Compliance**: Many jurisdictions require educational record retention
- **Safety**: Prevents accidental data loss by users
- **Control**: Centralized account management through administrators

## Future Options

### If Self-Deletion is Re-enabled
1. Remove the `abort(403)` in ProfileController
2. Change `@if(false)` to `@if(!auth()->user()->isAdmin())`
3. Consider adding:
   - Cooling-off period
   - Email confirmation
   - Data export before deletion
   - Soft deletes for recovery

### Alternative Implementations
1. **Request Deletion**: User requests, admin approves
2. **Soft Delete**: Deactivate account instead of hard delete
3. **GDPR Compliance**: Anonymize data instead of deletion
4. **Archive System**: Move to cold storage instead of delete

## Related Files
- `/routes/web.php` - Route definition (line 95)
- `/app/Http/Controllers/ProfileController.php` - Controller logic (lines 40-67)
- `/resources/views/profile/edit.blade.php` - View template (lines 20-28)
- `/resources/views/profile/partials/delete-user-form.blade.php` - Delete form partial

## Lessons Learned

### Key Takeaways
1. **Not all missing routes are bugs** - Some are intentional policy decisions
2. **Document administrative decisions** - Prevents confusion during debugging
3. **Preserve removed code** - Makes re-enabling features easier
4. **Multi-layer protection** - UI hiding alone isn't enough for security
5. **Consider business logic** - LMS platforms have different needs than general apps

### Best Practices
- Always document when features are intentionally disabled
- Keep routes defined even if functionality is restricted
- Use clear error messages when blocking access
- Preserve original code in comments for future reference

## Final Status
✅ Route exists (no more 404 errors)  
✅ Functionality properly restricted  
✅ Clear documentation of policy decision  
✅ Easy to re-enable if policy changes  
✅ Admin deletion still works through admin panel  

---

**Policy Owner**: GradeShark Administration  
**Decision Date**: Pre-fork (inherited from MedComic)  
**Last Review**: August 11, 2025  
**Next Review**: When implementing GDPR compliance features