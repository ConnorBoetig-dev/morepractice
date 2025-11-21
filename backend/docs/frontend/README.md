# Frontend Developer Guide

Welcome! This directory contains everything you need to integrate with the Billings API.

## 📚 Documentation Index

1. **[API Overview](./01-api-overview.md)** - Start here! High-level architecture and core concepts
2. **[Authentication](./02-authentication.md)** - JWT authentication, token management, and auth flows
3. **[Error Handling](./03-error-handling.md)** - Consistent error responses and error code reference
4. **[Endpoints Reference](./04-endpoints-reference.md)** - Complete API endpoint documentation with examples
5. **[Data Models](./05-data-models.md)** - Request/response schemas and data structures
6. **[Integration Guide](./06-integration-guide.md)** - Step-by-step integration instructions
7. **[Security Best Practices](./07-security-best-practices.md)** - Frontend security guide (NEW!)

## 🚀 Quick Start

```javascript
// 1. User signup
const response = await fetch('http://localhost:8000/api/v1/auth/signup', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    username: 'johndoe',
    password: 'SecurePass123!'
  })
});
const { access_token } = await response.json();

// 2. Make authenticated requests
const bookmarks = await fetch('http://localhost:8000/api/v1/bookmarks', {
  headers: {
    'Authorization': `Bearer ${access_token}`
  }
});
```

## 🔗 API Base URL

- **Development**: `http://localhost:8000`
- **Production**: TBD

## 🛠️ Interactive API Docs

While the API is running, you can explore interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 💡 Key Principles

- All responses are JSON
- All timestamps are ISO 8601 UTC
- All errors follow consistent format
- Authentication uses Bearer tokens
- Rate limiting is IP-based for public endpoints, user-based for authenticated endpoints

## 📞 Support

Questions? Issues? Contact the backend team or open an issue.
