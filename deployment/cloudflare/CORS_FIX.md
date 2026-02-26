# CORS Fix for Cloudflare

If you get "No 'Access-Control-Allow-Origin' header" when the driver/admin calls the API, the preflight OPTIONS request may not be reaching your backend. Try these:

## 1. Cloudflare Access (Zero Trust)

If **ambu.cfvision.in** is protected by Cloudflare Access, OPTIONS requests fail because browsers don't send cookies with preflight. Fix:

- Go to **Zero Trust** → **Access** → **Applications**
- Edit the application for `ambu.cfvision.in`
- Add a **Bypass** rule: Method equals `OPTIONS` → Bypass

Or create a rule that allows unauthenticated OPTIONS.

## 2. Transform Rule (add CORS at the edge)

Add a **Transform Rule** so Cloudflare adds CORS headers before the request hits your origin:

1. Go to **Rules** → **Transform Rules** → **Modify Response Header**
2. Create rule:
   - **Name:** Add CORS headers
   - **When:** `(http.host eq "ambu.cfvision.in")`
   - **Then:** Set static header
     - `Access-Control-Allow-Origin` = `https://driver.cfvision.in` (or use multiple rules for each origin)
     - `Access-Control-Allow-Methods` = `GET, POST, PUT, PATCH, DELETE, OPTIONS`
     - `Access-Control-Allow-Headers` = `Content-Type, Authorization`
     - `Access-Control-Allow-Credentials` = `true`

3. For **OPTIONS** requests specifically, add a **Config Transform** or **Custom Response** that returns 200 with these headers (so OPTIONS never hits the origin).

## 3. Verify backend is reachable

```bash
curl -I https://ambu.cfvision.in/health
```

You should get 200. If you get 403 or 502, the tunnel or Access is blocking.
