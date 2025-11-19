# ============================================
# SECURITY HEADERS MIDDLEWARE
# ============================================
# This middleware adds security-related HTTP headers to all responses
# to protect against common web vulnerabilities
#
# Headers added:
# - X-Content-Type-Options: Prevents MIME sniffing attacks
# - X-Frame-Options: Prevents clickjacking attacks
# - X-XSS-Protection: Enables browser XSS filtering
# - Strict-Transport-Security: Enforces HTTPS connections
# - Content-Security-Policy: Prevents XSS and injection attacks
# - Referrer-Policy: Controls referrer information leakage
# - Permissions-Policy: Controls browser features and APIs

from starlette.types import ASGIApp, Message, Receive, Scope, Send
import os


class SecurityHeadersMiddleware:
    """
    Add security headers to all HTTP responses

    This middleware implements OWASP security best practices:
    https://owasp.org/www-project-secure-headers/
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_with_headers(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))

                # Helper function to add header if not already present
                def add_header(name: str, value: str) -> None:
                    header_name = name.lower().encode()
                    # Check if header already exists
                    if not any(h[0].lower() == header_name for h in headers):
                        headers.append((name.encode(), value.encode()))

                # ============================================
                # PREVENT MIME SNIFFING
                # ============================================
                # Prevents browsers from interpreting files as a different MIME type
                # Example: Prevents .txt file from being executed as JavaScript
                add_header("X-Content-Type-Options", "nosniff")

                # ============================================
                # PREVENT CLICKJACKING
                # ============================================
                # Prevents your site from being embedded in an iframe on malicious sites
                # Options: DENY (never allow), SAMEORIGIN (only same domain)
                add_header("X-Frame-Options", "DENY")

                # ============================================
                # XSS PROTECTION (Legacy browsers)
                # ============================================
                # Enables browser's built-in XSS filter (legacy browsers)
                # Modern browsers use CSP instead, but this adds defense-in-depth
                add_header("X-XSS-Protection", "1; mode=block")

                # ============================================
                # ENFORCE HTTPS (HSTS)
                # ============================================
                # Tells browsers to only connect via HTTPS for the next year
                # includeSubDomains: Apply to all subdomains
                # preload: Allow inclusion in browser HSTS preload lists
                #
                # NOTE: Only enable in production with valid SSL certificate!
                # Disabled by default to allow local development on HTTP
                if os.getenv("ENABLE_HSTS", "false").lower() == "true":
                    add_header("Strict-Transport-Security",
                              "max-age=31536000; includeSubDomains; preload")

                # ============================================
                # CONTENT SECURITY POLICY (CSP)
                # ============================================
                # Prevents XSS attacks by controlling what resources can be loaded
                #
                # Policy breakdown:
                # - default-src 'self': Only load resources from same origin by default
                # - script-src 'self' 'unsafe-inline': Allow inline scripts (needed for some frameworks)
                # - style-src 'self' 'unsafe-inline': Allow inline styles (needed for some frameworks)
                # - img-src 'self' data: https:: Allow images from same origin, data URIs, and HTTPS
                # - font-src 'self' data:: Allow fonts from same origin and data URIs
                # - connect-src 'self': Only allow AJAX/WebSocket to same origin
                # - frame-ancestors 'none': Don't allow embedding in iframes (redundant with X-Frame-Options)
                # - base-uri 'self': Restrict <base> tag to same origin
                # - form-action 'self': Only allow form submissions to same origin
                #
                # NOTE: Adjust this policy based on your frontend needs
                # For example, if using CDNs, add their domains to script-src/style-src
                csp_policy = (
                    "default-src 'self'; "
                    "script-src 'self' 'unsafe-inline'; "
                    "style-src 'self' 'unsafe-inline'; "
                    "img-src 'self' data: https:; "
                    "font-src 'self' data:; "
                    "connect-src 'self'; "
                    "frame-ancestors 'none'; "
                    "base-uri 'self'; "
                    "form-action 'self'"
                )
                add_header("Content-Security-Policy", csp_policy)

                # ============================================
                # REFERRER POLICY
                # ============================================
                # Controls how much referrer information is sent with requests
                # strict-origin-when-cross-origin: Send full URL for same-origin,
                # only origin for cross-origin HTTPS, nothing for HTTP
                add_header("Referrer-Policy", "strict-origin-when-cross-origin")

                # ============================================
                # PERMISSIONS POLICY (Feature Policy)
                # ============================================
                # Controls which browser features and APIs can be used
                # This prevents malicious third-party scripts from accessing sensitive features
                #
                # Disabled features:
                # - geolocation: Location tracking
                # - microphone: Audio recording
                # - camera: Video recording
                # - payment: Payment Request API
                # - usb: USB device access
                # - magnetometer: Device orientation sensors
                # - gyroscope: Device motion sensors
                # - accelerometer: Device motion sensors
                permissions_policy = (
                    "geolocation=(), "
                    "microphone=(), "
                    "camera=(), "
                    "payment=(), "
                    "usb=(), "
                    "magnetometer=(), "
                    "gyroscope=(), "
                    "accelerometer=()"
                )
                add_header("Permissions-Policy", permissions_policy)

                # ============================================
                # REMOVE SERVER HEADER
                # ============================================
                # Remove server header to avoid revealing server technology
                # This makes fingerprinting attacks slightly harder
                headers[:] = [h for h in headers if h[0].lower() != b"server"]

                # Update message with new headers
                message["headers"] = headers

            await send(message)

        await self.app(scope, receive, send_with_headers)
