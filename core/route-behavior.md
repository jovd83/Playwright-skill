# Route Behavior and Parity

> **When to use**: Validating complex navigation, redirects, and ensuring consistency between different route representations (e.g., UUID-based URLs vs alias-based slugs).

## Patterns

### 1. URL Settling and Redirects

Never assert on a URL immediately after a click if a redirect might happen. Use `page.waitForURL()` or a regex assertion.

```typescript
// GOOD: Wait for the URL to settle after potentially multiple redirects
await page.getByRole('button', { name: 'Submit' }).click();
await page.waitForURL('**/dashboard', { waitUntil: 'networkidle' });
expect(page.url()).toContain('/dashboard');
```

### 2. Route Parity (UUID vs Slugs)

Ensure that different ways of accessing the same resource result in the same UI state.

```typescript
test('route parity: uuid vs alias', async ({ page }) => {
  const resourceUuid = '123e4567-e89b-12d3-a456-426614174000';
  const resourceAlias = 'my-cool-resource';

  // Check UUID route
  await page.goto(`/resources/${resourceUuid}`);
  await expect(page.getByRole('heading')).toHaveText('Resource Details');

  // Check Alias route
  await page.goto(`/resources/${resourceAlias}`);
  await expect(page.getByRole('heading')).toHaveText('Resource Details');
  
  // Verify they both resolve to the same canonical data-testid
  await expect(page.getByTestId('resource-id')).toHaveAttribute('data-id', resourceUuid);
});
```

### 3. Negative Path Parity

Ensure `404` and `403` handlers behave consistently across similar routes.

```typescript
const routesToTest = [
  '/admin/settings',
  '/admin/users',
  '/admin/billing'
];

for (const route of routesToTest) {
  test(`unauthorized access to ${route} redirects to login`, async ({ page }) => {
    // Unauthenticated context
    await page.goto(route);
    await page.waitForURL('**/login');
  });
}
```

## Checklist

- [ ] **Redirect Wait**: Used `page.waitForURL()` for multi-step redirects.
- [ ] **Parser Helpers**: Created utility functions to extract parameters from current URL for assertions.
- [ ] **Fallback Validation**: Verified that invalid UUIDs or expired slugs trigger correct 404/Fallback UI rather than a crash.
- [ ] **Dynamic State**: Verified that query parameters (e.g., `?tab=settings`) are preserved or correctly handled during navigation.
