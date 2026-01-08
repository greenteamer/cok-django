# Caching & Static Files Strategy

This guide explains the static file serving strategy, specifically how we handle caching and versioning to prevent "stale content" issues with Nginx and Cloudflare.

## The Caching Problem

By default, Nginx and Cloudflare aggressively cache static files (CSS, JS, Images) to improve performance. This creates a problem during deployment:
- You deploy new CSS.
- The file name (`styles.css`) remains the same.
- Cloudflare/Nginx serves the *old* file from cache.
- Users see a broken or outdated site.

## The Solution: ManifestStaticFilesStorage

We use Django's `ManifestStaticFilesStorage` to implement **Cache Busting via Hashing**.

### Configuration
In `config/settings.py`:
```python
STORAGES = {
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage",
    },
}
```

### How it works
1. **Hashing:** When `collectstatic` runs, it calculates a hash of the file content.
2. **Renaming:** It creates a copy of the file with the hash in the name.
   - Source: `styles.css`
   - Result: `styles.5f3a2b.css`
3. **Manifest:** It creates `staticfiles.json` mapping the original name to the hashed name.
4. **Serving:** The `{% static %}` template tag looks up the new name in the manifest.

### Deployment Implications

Because filenames change on every content update:
1. **Atomic Deployments:** Users instantly see the new version.
2. **Cloudflare Friendly:** Cloudflare treats `styles.5f3a2b.css` as a completely new file and fetches it immediately. No "Purge Cache" required.
3. **Requirement:** You **MUST** run `collectstatic` during every deployment (handled by `make deploy-static`).

## Troubleshooting

### "Missing staticfiles manifest entry"
If you see this error (ValueError), it means a template is referencing a static file that doesn't exist or hasn't been processed by `collectstatic`.
**Fix:** Run `make deploy-static` locally or on the server.

### 404 on Static Files
If `styles.hash.css` returns 404:
1. Ensure `collectstatic` finished successfully.
2. Check Nginx permissions (`make fix-permissions`).
