# Changelog

## Recent Changes

### Login Page Fixes (2026-05-02)

**Issue**: Login page had duplicate functions causing JavaScript errors.

**Changes Made**:

1. **render.js** - Fixed duplicate function definitions:
   - Removed duplicate `selectUserByIndex` (was defined twice)
   - Removed duplicate `updateRoleBadge` (was defined twice)  
   - Fixed `renderNav()` to properly update nav links based on role
   - Added `renderAll()` function that was missing

2. **main.js** - Removed duplicate local functions:
   - Removed local `selectUserByIndex` - now imports from `render.js`
   - Removed local `updateRoleBadge` - now imports from `render.js`
   - Updated imports to include `selectUserByIndex` and `updateRoleBadge`

**Before**: Both `render.js` and `main.js` had their own copies of `selectUserByIndex` and `updateRoleBadge`, causing duplicate definition errors.

**After**: Functions are defined once in `render.js` and imported where needed in `main.js`.