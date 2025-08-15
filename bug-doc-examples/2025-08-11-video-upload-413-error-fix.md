# RESOLVED: Video Upload HTTP 413 Error - File Size Limits

## 🚨 Issue Summary

**Date Identified**: August 11, 2025  
**Date Resolved**: August 11, 2025  
**Severity**: High - Video/large file uploads completely blocked  
**Affected Areas**: All file upload functionality (videos, ZIP files, large PDFs)  
**Error**: HTTP 413 "Payload Too Large"  

---

## 📋 Problem Description

### Symptoms
1. **HTTP 413 error** when uploading MP4 video files
2. **Upload fails immediately** at web server level
3. **Error occurs before reaching Laravel** application
4. **Affects all file types** over ~1-2MB

### User Impact
- Unable to upload course videos
- Unable to upload game ZIP files
- Unable to upload large PDF materials
- Core LMS functionality severely limited

---

## 🔍 Root Cause Analysis

### The Configuration Mismatch

The issue was caused by a **three-layer configuration mismatch** between:

1. **Laravel Application Expectations**
2. **PHP Configuration Limits**  
3. **Nginx Web Server Limits**

### Layer 1: Laravel Validation Rules
```php
// Laravel expected these limits:
'file' => 'required|file|mimes:jpg,jpeg,png,webp,pdf,mp4,zip,txt|max:20480'  // 20MB
'game_zip' => 'nullable|file|mimes:zip|max:51200'                            // 50MB
'asset_file' => 'required|file|mimes:jpg,jpeg,png,gif,webp,svg,mp4,pdf,zip|max:20480' // 20MB
```

### Layer 2: PHP Configuration (Too Low!)
```ini
# Production PHP settings were:
upload_max_filesize = 2M    # ❌ Only 2MB allowed!
post_max_size = 8M          # ❌ Only 8MB for entire POST!
```

### Layer 3: Nginx Configuration (Blocking Everything!)
```nginx
# Nginx had NO client_max_body_size set
# This defaults to ~1MB!
# Result: Nginx rejected uploads before PHP even saw them
```

### The Request Flow Problem
```
User uploads 10MB video
    ↓
Nginx checks size → EXCEEDS 1MB default → Returns 413 ❌
    ↓
Never reaches PHP
    ↓
Never reaches Laravel
```

---

## ✅ Solution Implemented

### Step 1: Diagnosed the Issue
Used SSH to check actual server limits:
```bash
# Checked PHP limits
php -i | grep -E 'post_max_size|upload_max_filesize'
# Result: upload_max_filesize => 2M, post_max_size => 8M

# Checked Nginx config
grep 'client_max_body_size' /etc/nginx/sites-enabled/gradeshark.com
# Result: Not found (using 1MB default)
```

### Step 2: Updated PHP Configuration
In Laravel Forge → Server → PHP:

**Via Forge UI Fields:**
- Max File Upload Size: `55` MB
- Max Execution Time: `300` seconds

**Via PHP.ini Edit:**
```ini
upload_max_filesize = 55M    # Allows 50MB files + buffer
post_max_size = 60M          # Must be larger than upload_max
max_execution_time = 300     # 5 minutes for slow uploads
max_input_time = 300         # 5 minutes input processing
memory_limit = 512M          # Sufficient for large files
```

### Step 3: Updated Nginx Configuration
In Laravel Forge → Sites → gradeshark.com → Nginx Configuration:

```nginx
server {
    # ... existing config ...
    root /home/forge/gradeshark.com/public;
    
    # Added this critical line:
    client_max_body_size 60M;
    
    # ... rest of config ...
}
```

### Step 4: Applied Configuration Changes
1. Clicked **Update** in PHP settings (auto-restarts PHP-FPM)
2. Clicked **Save** in Nginx config (auto-reloads Nginx)
3. Verified via Services → Nginx → **Reload** button

---

## 📊 Configuration Alignment

### Before Fix (Misaligned)
| Layer | Limit | Result |
|-------|-------|---------|
| Laravel | 20-50MB | Expects large files ✓ |
| PHP | 2MB | Blocks at PHP layer ✗ |
| Nginx | ~1MB | Blocks at server layer ✗ |

### After Fix (Properly Aligned)
| Layer | Limit | Result |
|-------|-------|---------|
| Laravel | 20-50MB | Validates appropriately ✓ |
| PHP | 55MB | Allows all expected sizes ✓ |
| Nginx | 60MB | Passes through to PHP ✓ |

---

## 🔧 Technical Details

### Why These Specific Limits?

1. **55MB PHP `upload_max_filesize`**
   - Covers 50MB game ZIPs
   - Provides 5MB buffer for overhead
   
2. **60MB PHP `post_max_size`**
   - Must exceed upload_max_filesize
   - Accounts for form data + file
   
3. **60MB Nginx `client_max_body_size`**
   - Must match or exceed PHP limits
   - Prevents Nginx from blocking valid uploads

4. **300s Execution/Input Time**
   - Allows slow connections to complete
   - Prevents timeout on large files

### Configuration Hierarchy
```
Nginx (Gateway) → PHP (Processor) → Laravel (Application)
     60MB      →      55MB       →     20-50MB
     
Each layer must allow AT LEAST what the next layer expects
```

---

## 🛠️ Debugging Commands Used

### Checking Current Limits
```bash
# PHP limits
ssh forge@server "php -i | grep -E 'upload_max_filesize|post_max_size'"

# Nginx configuration
ssh forge@server "grep 'client_max_body_size' /etc/nginx/sites-enabled/gradeshark.com"

# Verify Nginx config is valid
ssh forge@server "sudo nginx -t"

# Check when Nginx was last reloaded
ssh forge@server "ps aux | grep '[n]ginx: master'"
```

### Verification After Fix
```bash
# Confirm PHP changes
php -i | grep -E 'upload_max_filesize|post_max_size'
# Result: upload_max_filesize => 55M, post_max_size => 60M

# Confirm Nginx changes
grep 'client_max_body_size' /etc/nginx/sites-enabled/gradeshark.com
# Result: client_max_body_size 60M;

# Test with curl (optional)
curl -X POST -F "file=@large_video.mp4" https://gradeshark.com/upload
```

---

## 💡 Lessons Learned

### What Went Wrong
1. **Default server limits too conservative** - Forge defaults assume small files
2. **Multiple configuration layers** - Each layer can block uploads independently
3. **Forge UI vs config files** - UI fields override manual PHP.ini edits
4. **Silent Nginx blocking** - Nginx returns 413 before request reaches application logs

### Best Practices Established
1. **Always check all three layers** when debugging upload issues
2. **Use Forge UI fields** instead of manual PHP.ini edits when available
3. **Align limits hierarchically**: Nginx ≥ PHP ≥ Laravel
4. **Test with actual files** after configuration changes
5. **Document expected file sizes** in application requirements

### Prevention Measures
1. **Set limits during initial deployment** - Don't rely on defaults
2. **Monitor upload failures** - Log 413 errors for early detection
3. **Display user-friendly limits** - Show max file size in upload UI
4. **Progressive enhancement** - Check file size client-side before upload

---

## 📝 Configuration Reference

### Laravel Forge Settings Location
- **PHP Settings**: Server → PHP → Max File Upload Size & Max Execution Time
- **Nginx Settings**: Sites → [site-name] → Nginx Configuration

### Manual Configuration Paths (if needed)
```bash
# PHP configuration
/etc/php/8.3/fpm/php.ini

# Nginx site configuration  
/etc/nginx/sites-available/gradeshark.com
/etc/nginx/sites-enabled/gradeshark.com

# Service control
sudo service php8.3-fpm restart
sudo service nginx reload
```

### Environment Considerations
```env
# These Laravel env variables are NOT needed
# (Laravel uses PHP's limits automatically)
# UPLOAD_MAX_FILESIZE=55M  # Don't add these
# POST_MAX_SIZE=60M         # Don't add these
```

---

## 🎯 Testing Checklist

After implementing the fix:

- [x] Small image upload (<2MB) - Should work
- [x] Large image upload (5MB) - Should work  
- [x] Video file upload (10-20MB) - Should work
- [x] Game ZIP upload (30-50MB) - Should work
- [x] Oversized file (>55MB) - Should show Laravel validation error
- [x] Check no 413 errors in browser console
- [x] Verify uploads actually save to S3

---

## 🚦 Success Metrics

### Before Fix
- ❌ 413 error on video uploads
- ❌ 413 error on files over ~1MB
- ❌ Uploads fail at Nginx level
- ❌ No error logging in Laravel

### After Fix
- ✅ Videos up to 20MB upload successfully
- ✅ Game ZIPs up to 50MB upload successfully
- ✅ Proper validation messages for oversized files
- ✅ All uploads reach Laravel for processing
- ✅ Files successfully stored in S3

---

## 🔗 Related Issues

- [RESOLVED_WEBP_CRASH.md](./RESOLVED_WEBP_CRASH.md) - S3 upload error handling
- [Admin Manual - File Storage](../../admin/COMPLETE_ADMIN_MANUAL.md#file-storage)
- [Laravel File Upload Documentation](https://laravel.com/docs/validation#validating-files)

---

## 📚 Additional Resources

### Understanding the Error Chain
1. **Client** → Sends multipart/form-data with file
2. **Cloudflare** → Has own limits (100MB free plan)
3. **Nginx** → Checks `client_max_body_size`
4. **PHP-FPM** → Checks `upload_max_filesize` and `post_max_size`
5. **Laravel** → Validates against rules (max:20480)
6. **S3** → Accepts files up to 5GB (single PUT)

### Quick Reference Table
| File Type | Laravel Limit | Use Case |
|-----------|--------------|-----------|
| Images | 2MB | Course thumbnails |
| Assets | 20MB | PDFs, videos, documents |
| Videos | 20MB | Lesson content |
| Game ZIPs | 50MB | Interactive content |

---

## 🎓 Key Takeaways

1. **HTTP 413 errors occur at the web server level** - Check Nginx first
2. **Laravel Forge UI fields override PHP.ini** - Use UI when available
3. **Configuration must align across all layers** - Nginx → PHP → Laravel
4. **Always reload/restart services** - Config changes need service reload
5. **Test with realistic file sizes** - Don't assume small test files represent real usage

---

**Issue resolved by**: Claude (AI Assistant)  
**Date resolved**: August 11, 2025  
**Time to resolution**: ~30 minutes after proper diagnosis  
**Configuration impact**: Server now properly handles files up to 55MB  

*The platform now fully supports video uploads, game packages, and large educational materials as originally intended.*