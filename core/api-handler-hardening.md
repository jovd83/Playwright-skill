# API Handler Hardening (Unit Testing Endpoints)

> **When to use**: Testing the business logic of API endpoints in isolation before performing end-to-end (E2E) testing. This applies regardless of your backend language (Node.js, Python, Go, Java, etc.).

## Core Principles

1. **Request/Response Isolation**: Do not start a real web server. Instead, invoke the handler function directly with a simulated request object and capture the response.
2. **Deterministic State via Mocking**: Mock all external dependencies (Database, Auth Providers, Third-party APIs) so the test is predictable and fast.
3. **Logic Coverage**: Focus on input validation, authorization checks, and conditional business logic branches.
4. **Contract Verification**: Ensure the response structure (JSON schema) and HTTP status codes match the agreed-on API contract.

## Anatomy of a Handler Test

Regardless of the framework, every handler test follows this pattern:

1. **Setup Context**: Mock database results, user sessions, and environment variables.
2. **Simulate Request**: Construct a request object with specific headers, query params, and body.
3. **Execution**: Call the handler function.
4. **Assertions**: 
   - Verify the **HTTP Status Code** (e.g., 201 for Created).
   - Verify the **Response Body** (e.g., correct IDs, transformed data).
   - Verify **Side Effects** (e.g., were the correct DB methods called with expected data?).

## Error Taxonomy Validation

Standardize your error codes to ensure client-side tests (like Playwright) and front-end code can handle failures predictably.

Category | HTTP Code | Use Case
---|---|---
**Client Error** | `400 Bad Request` | Validation failure, missing fields, malformed JSON
**Unauthorized** | `401 Unauthorized` | No authentication provided or invalid credentials
**Forbidden** | `403 Forbidden` | Authenticated, but lacking permission for this resource
**Not Found** | `404 Not Found` | The requested resource ID does not exist
**Server Error** | `500 Internal Error` | Unhandled exceptions, database connection loss

---

## Reference Implementation (Example: Node.js / Next.js)

### Mocking the Data Layer
In Node.js, libraries like `vitest-mock-extended` or `jest.mock` allow you to replace a database client (like Prisma) with a mock.

```typescript
// Mock setup
vi.mock('../../lib/db', () => ({
  default: {
    user: {
      create: vi.fn().mockResolvedValue({ id: '1', email: 'test@example.com' })
    }
  }
}));
```

### Testing the Handler
```typescript
it('should create a user and return 201', async () => {
  const req = new SimulatedRequest({
    method: 'POST',
    body: { email: 'test@example.com' }
  });

  const res = await userHandler.POST(req);
  const data = await res.json();

  expect(res.status).toBe(201);
  expect(data.id).toBe('1');
});
```

## Checklist

- [ ] **Dependency Isolation**: All DB, Auth, and External API calls are mocked or used via an interface.
- [ ] **Input Validation**: Verified that missing or malformed input correctly returns a `400`.
- [ ] **Auth Enforcement**: Verified that unauthorized requests return `401` or `403`.
- [ ] **Contract Consistency**: Response JSON matches the schema used by the frontend.
- [ ] **Error Details**: Error responses provide enough context for debugging without leaking system internals.
