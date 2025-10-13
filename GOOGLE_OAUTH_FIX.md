# Google OAuth Redirect URI Fix

**Issue:** `Error 400: redirect_uri_mismatch`

**Error Message:**
```
You can't sign in to this app because it doesn't comply with Google's OAuth 2.0 policy.
Request details: redirect_uri=https://lodgeick.com/oauth/callback
```

---

## Root Cause

The redirect URI registered in your Google Cloud Console doesn't match what the backend is sending. The backend has been fixed to use `https://lodgeick.com/oauth/callback`, but your Google OAuth credentials need to be updated.

---

## Fix Instructions

### Step 1: Go to Google Cloud Console

1. Open [Google Cloud Console - Credentials](https://console.cloud.google.com/apis/credentials)
2. Make sure you have the correct project selected (the one with your OAuth credentials)

### Step 2: Find Your OAuth Client ID

Look for your OAuth 2.0 Client ID in the list. It should be named something like:
- "Lodgeick"
- "Lodgeick Local"
- "Web client" (default name)

Click on the **name** of the OAuth client to edit it.

### Step 3: Update Authorized Redirect URIs

In the OAuth client configuration:

1. Scroll down to **"Authorized redirect URIs"**

2. You'll see the current redirect URI(s). **Add or update** to include:
   ```
   https://lodgeick.com/oauth/callback
   ```

3. **Important:** Make sure it's EXACTLY this URL:
   - Protocol: `https://` (not http)
   - Domain: `lodgeick.com` (no trailing slash)
   - Path: `/oauth/callback` (not `/api/method/...`)

4. If you see an old redirect URI like:
   ```
   https://lodgeick.com/api/method/lodgeick.api.oauth.oauth_callback
   ```
   You can **remove it** (it's the old one that doesn't work anymore).

### Step 4: Save Changes

1. Click **"Save"** at the bottom of the page
2. Wait a few seconds for changes to propagate

### Step 5: Test OAuth Flow

1. Go back to Lodgeick
2. Try connecting Google again via Quick Start
3. The OAuth flow should now work correctly

---

## For Local Development

If you're testing on `localhost`, you also need to add the local redirect URI:

```
http://localhost:8080/oauth/callback
```

Or whatever port you're using for local development.

---

## Expected Redirect URIs

Your Google OAuth client should have these redirect URIs:

**Production:**
```
https://lodgeick.com/oauth/callback
```

**Local Development (if applicable):**
```
http://localhost:8080/oauth/callback
http://localhost:8000/oauth/callback
http://home.localhost:8080/oauth/callback
```

---

## Verification

After making these changes, the OAuth flow should work as follows:

1. User clicks "Connect with Google" (Quick Start or Manual)
2. User is redirected to Google's authorization page
3. User approves permissions
4. **Google redirects to:** `https://lodgeick.com/oauth/callback?code=...&state=...`
5. Frontend Vue page receives the callback
6. Frontend calls backend API to exchange code for tokens
7. Success! User is connected

---

## Still Having Issues?

### Check Your OAuth Credentials

Make sure the `client_id` and `client_secret` in your site config match the OAuth client you just updated:

```bash
# Check current credentials
cat sites/lodgeick.com/site_config.json | grep -A 2 "google_client_id"
```

The client ID should match the one from Google Cloud Console.

### Check Client ID Match

1. In Google Cloud Console, copy the **Client ID** from your OAuth client
2. It should look like: `993147492465-17qcog97vbi2vv3i2a2bt5pvmcav83pq.apps.googleusercontent.com`
3. Compare with your site_config.json `google_client_id`
4. They must be **exactly the same**

### Multiple OAuth Clients

If you have multiple OAuth clients in Google Cloud Console, make sure you're updating the correct one. The client ID in your config should match the client you're editing.

---

## Backend Changes Made

The backend has been updated in commit `1ecc2a9`:

**File:** `lodgeick/api/oauth.py`

**Changes:**
- `build_auth_url()` - Uses `/oauth/callback` instead of `/api/method/...`
- `exchange_code_for_tokens()` - Uses same redirect URI

This ensures the redirect URI sent to Google matches what's registered in Google Cloud Console.

---

## Summary

✅ **Backend is fixed** - Uses correct redirect URI
⚠️ **Google Console needs update** - Add `https://lodgeick.com/oauth/callback` as authorized redirect URI
✅ **After update** - OAuth flow will work correctly

---

**Last Updated:** 2025-10-14
**Related Commits:** `1ecc2a9`, `8736032`
