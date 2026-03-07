# Contract-First Mocking (Temporary Bridge for Frontend Development)

> [!IMPORTANT]
> **Mocking is a last resort.** Always prefer real End-to-End (E2E) verification against a real backend whenever possible. This guide is specifically for the period *before* the backend is available or when hitting the real backend is physically impossible.

> **When to use**: **Only** when frontend development must start before the backend implementation is ready, or to test specialized error states (4xx/5xx) that are impossible to trigger reliably on a real environment.

## The E2E-First Workflow

1. **Agree on the Contract**: Collaborate with backend developers to define the API shape.
2. **Implement Temporary Skeleton Mocks**: Create Playwright routes to unblock frontend development.
3. **Develop Frontend Logic**: Use the mocks to build UI components and initial test logic.
4. **Final Verification (The Goal)**: Transition **100%** to real E2E tests once the backend is ready. Verification is incomplete until it has passed against real services.

---

## 1. Defining the Contract

Use a shared source of truth.

- **OpenAPI / Swagger**: Generate types or mock data from a `.yaml` file.
- **TypeScript Interfaces**: Share a common `types` package between frontend and backend.
- **JSON Schemas**: Ensure the mock data matches the expected production output.

---

## 2. Environment-Driven Toggling

Configure your project to easily switch between **Real** and **Mocked** modes using environment variables.

### Config Setup (`playwright.config.ts`)

```typescript
export default defineConfig({
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
  },
  // Define a custom metadata field for mocking
  metadata: {
    useMocks: process.env.USE_MOCKS === 'true',
  }
});
```

### Global Fixture for Toggling

Create a fixture that applies mocks only if `USE_MOCKS` is enabled.

```typescript
// tests/fixtures/contract-mocks.ts
import { test as base } from '@playwright/test';

export const test = base.extend({
  page: async ({ page }, use, testInfo) => {
    const useMocks = testInfo.project.metadata?.useMocks || process.env.USE_MOCKS === 'true';

    if (useMocks) {
      console.log('--- RUNNING WITH MOCKS ---');
      await page.route('**/api/v1/users', (route) => {
        route.fulfill({
          status: 200,
          json: [{ id: '1', name: 'Contract User', role: 'Developer' }]
        });
      });
      // Add other contract-based routes here
    }

    await use(page);
  },
});
```

---

## 3. Refactoring from Mock to Real

When the backend implementation is ready, you don't need to rewrite your tests. Instead:

### Phase A: Parallel Runs
Run your tests twice in CI: 
- Once with `USE_MOCKS=true` (fast feedback on UI logic).
- Once with `USE_MOCKS=false` against a staging backend (integration confidence).

### Phase B: Hybrid Mocking (The "Shim" Pattern)
Use `route.fetch()` to let real calls through, but fall back to mocks for endpoints that aren't ready or for specific error states.

```typescript
await page.route('**/api/v1/**', async (route) => {
  try {
    const response = await route.fetch();
    if (response.status() === 404 || response.status() === 501) {
      // Fallback to mock if endpoint is not implemented yet
      return route.fulfill({ json: getMockData(route.request().url()) });
    }
    await route.fulfill({ response });
  } catch (e) {
    // Fallback if backend is down
    return route.fulfill({ json: getMockData(route.request().url()) });
  }
});
```

### Phase C: Mock Decay Audit
Periodically disable mocks to see which tests fail. This identifies where the backend implementation has diverged from the original contract.

---

## Checklist

- [ ] **E2E verification**: Ensure every mocked scenario has a corresponding run configured against the real backend as part of integration verification.
- [ ] **Contract Versioning**: Mocks are updated if and when the API version changes.
- [ ] **Data Parity**: Mock data uses realistic values (e.g., valid UUIDs, real-looking emails).
- [ ] **Switchable Config**: The `USE_MOCKS` flag is documented and works in both local and CI environments.
- [ ] **Mock Decay Audit**: Regularly disable mocks to catch drift between the contract and the implementation.
