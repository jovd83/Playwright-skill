# Locator Resilience and Strict Mode

> **When to use**: Dealing with multiple similar elements, localization variations, or strict-mode collisions in complex UIs.

## Patterns

### 1. Same-Label Multi-Surface Disambiguation

When a label like "Save" appears in both a sidebar and a main modal, use `locator.filter()` or container scoping.

```typescript
// BAD: Strict mode error if multiple "Save" buttons exist
await page.getByRole('button', { name: 'Save' }).click();

// GOOD: Scope to the active container
const modal = page.getByRole('dialog', { name: 'Edit User' });
await modal.getByRole('button', { name: 'Save' }).click();

// GOOD: Use filtering by visibility or other attributes
await page.getByRole('button', { name: 'Save' }).filter({ visible: true }).click();
```

### 2. Localization-Tolerant Locators

Avoid hardcoding strings when possible. Use `data-testid` or regex if the text varies slightly (e.g., "Save", "Speichern", "Enregistrer").

```typescript
// RESILIENT: Using regex for common variations
await page.getByRole('button', { name: /save|speichern|enregistrer/i }).click();

// BEST: Using a stable automation contract
await page.getByTestId('save-button').click();
```

### 3. Strict-Mode Collision Recovery

If a test fails with "strict mode violation: resolved to 3 elements", use this triage checklist:

1. **Check for hidden duplicates**: Is there a mobile version of the button also in the DOM?
2. **Check for stale elements**: Did the previous modal close but its markup remain?
3. **Use `.first()` / `.last()` only as a last resort**: It's usually better to be more specific.

```typescript
// TRIAGE EXAMPLE
// Violation: multiple <h1> found
const header = page.getByRole('heading', { level: 1 });

// Fix: specify which one by its parent's purpose
const mainContentHeader = page.getByRole('main').getByRole('heading', { level: 1 });
```

## Heuristics for Locator Precision

1. **Role + Name**: `getByRole('button', { name: 'Login' })`
2. **Role + Container**: `page.locator('form#login').getByRole('button')`
3. **Test ID**: `getByTestId('login-submit')`
4. **ARIA Attributes**: `getByRole('button').and(page.getByLabel('submit'))`

## Checklist

- [ ] **Strict Mode Audit**: Run tests with `expect(locator).toHaveCount(1)` to catch hidden duplicates.
- [ ] **Role Tightening**: Move from generic `locator('.btn')` to specific `getByRole('button')`.
- [ ] **Container Scoping**: Ensure every action happens within the intended UI surface.
