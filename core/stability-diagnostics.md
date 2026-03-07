# Stability Diagnostics and Flake Hardening

> **When to use**: Handling post-failure triage, hydration races, pointer interception, and optimistic UI timing issues.

## Error Context Triage Flow

When a test fails intermittently, follow this triage flow:

1. **Hydration Check**: Does the button exist but isn't "clickable" yet because the UI framework (e.g., React, Vue, Angular) hasn't hydrated?
   - *Fix*: Wait for a state change or an attribute that indicates readiness.
2. **Pointer Interception**: Is a loading spinner or another invisible overlay blocking the click?
1.  **Hydration Check**: Does the button exist but isn't "clickable" yet because the UI framework (e.g., React, Vue, Angular) hasn't hydrated?
    -   *Fix*: Wait for a state change or an attribute that indicates readiness.
2.  **Pointer Interception**: Is a loading spinner or another invisible overlay blocking the click?
    -   *Fix*: `await expect(page.getByTestId('spinner')).toBeHidden()`
3.  **Optimistic UI**: Did the UI update *before* the API call finished, causing the next action to fail when the API eventually errors?
    -   *Fix*: Wait for the network response before proceeding.

## Hydration-Safe Interactions

### Preflight Script (Example Implementation)
In hydration-heavy apps, `page.goto()` might return "ready" while the JS is still loading.

```typescript
// BAD: Click might happen before event listeners are attached
await page.goto('/');
await page.getByRole('button', { name: 'Menu' }).click();

// GOOD: Ensure the menu is actually interactive
await page.goto('/');
const menuBtn = page.getByRole('button', { name: 'Menu' });
await expect(menuBtn).toBeVisible();
await expect(menuBtn).toBeEnabled(); // Simple check for hydrated state
await menuBtn.click();
```

## Flake-Hardening Recipes

### 1. Pointer Interception Recovery

```typescript
// If an element is frequently intercepted:
await expect(async () => {
    // Attempt action
    await page.getByRole('button', { name: 'Save' }).click({ force: false });
}).toPass({
    intervals: [500, 1000, 2000],
    timeout: 10000
});
```

### 2. Optimistic UI Validation

```typescript
// Ensure the background request actually finished
const savePromise = page.waitForResponse('**/api/save');
await page.getByRole('button', { name: 'Save' }).click();
const response = await savePromise;
expect(response.status()).toBe(200);

// Now proceed to assert on the next page/state
await expect(page.getByText('Success')).toBeVisible();
```

## Run-Health Classification

Don't just look at Pass/Fail. Monitor these "health metrics":

- **Console Errors**: Are there `404` or `500` errors in the console during a "Passing" test?
- **Warning Count**: Is the app spamming "depreciated" warnings that slow down the run?
- **Rerun Policy**: If a test fails once but passes on retry, it's a **Flake**, not a **Pass**. Treat it as a bug.

## Checklist

- [ ] **Triage Context**: Captured trace and video for the failing run.
- [ ] **Timing Analysis**: Compared "Success" vs "Failure" network timelines.
- [ ] **Spinners & Overlays**: Explicitly waited for "Loading" states to resolve.
- [ ] **Optimistic Sync**: Verified that UI state reflects the backend truth.
