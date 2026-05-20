/**
 * tests/utils/qpilot-helpers.ts
 *
 * Shared Playwright utilities for QPilot-generated test scripts.
 * Import these in generated tests for common actions and assertions.
 */

import { Page, expect, Locator } from '@playwright/test'

// ── Navigation helpers ────────────────────────────────────────────

/**
 * Navigate to a URL and wait for the page to be fully loaded.
 */
export async function navigateTo(page: Page, path: string): Promise<void> {
  const baseUrl = process.env.BASE_URL || 'http://localhost:3000'
  await page.goto(`${baseUrl}${path}`)
  await page.waitForLoadState('networkidle')
}

// ── Form helpers ──────────────────────────────────────────────────

/**
 * Fill a form field by label text (accessible selector).
 */
export async function fillByLabel(page: Page, label: string, value: string): Promise<void> {
  await page.getByLabel(label, { exact: false }).fill(value)
}

/**
 * Click a button by its visible text.
 */
export async function clickButton(page: Page, text: string): Promise<void> {
  await page.getByRole('button', { name: text, exact: false }).click()
}

/**
 * Select an option from a dropdown by label.
 */
export async function selectOption(page: Page, label: string, value: string): Promise<void> {
  await page.getByLabel(label).selectOption(value)
}

// ── Assertion helpers ─────────────────────────────────────────────

/**
 * Assert the current URL contains the expected path.
 */
export async function assertUrl(page: Page, expectedPath: string): Promise<void> {
  await expect(page).toHaveURL(new RegExp(expectedPath.replace(/\//g, '\\/')))
}

/**
 * Assert text is visible on the page.
 */
export async function assertVisible(page: Page, text: string): Promise<void> {
  await expect(page.getByText(text, { exact: false }).first()).toBeVisible()
}

/**
 * Assert an element with a test ID is visible.
 */
export async function assertTestId(page: Page, testId: string): Promise<void> {
  await expect(page.getByTestId(testId)).toBeVisible()
}

/**
 * Assert a toast notification appears with the given text.
 */
export async function assertToast(page: Page, text: string): Promise<void> {
  await expect(page.getByRole('status').filter({ hasText: text })).toBeVisible({
    timeout: 5000,
  })
}

/**
 * Assert an input has a specific value.
 */
export async function assertInputValue(page: Page, label: string, value: string): Promise<void> {
  await expect(page.getByLabel(label, { exact: false })).toHaveValue(value)
}

// ── Wait helpers ──────────────────────────────────────────────────

/**
 * Wait for a network request to complete (useful after form submits).
 */
export async function waitForRequest(page: Page, urlPattern: RegExp): Promise<void> {
  await page.waitForResponse(resp => urlPattern.test(resp.url()) && resp.status() < 400)
}

/**
 * Wait for a loading spinner to disappear.
 */
export async function waitForLoading(page: Page): Promise<void> {
  const spinner = page.locator('[data-testid="loading"], .animate-spin').first()
  if (await spinner.isVisible().catch(() => false)) {
    await expect(spinner).not.toBeVisible({ timeout: 30000 })
  }
}

// ── Auth helpers ──────────────────────────────────────────────────

/**
 * Log in via the UI and wait for dashboard redirect.
 */
export async function loginAs(page: Page, email: string, password: string): Promise<void> {
  await navigateTo(page, '/auth/login')
  await fillByLabel(page, 'Email', email)
  await fillByLabel(page, 'Password', password)
  await clickButton(page, 'Sign in')
  await assertUrl(page, '/dashboard')
}

/**
 * Log in as the default admin user.
 */
export async function loginAsAdmin(page: Page): Promise<void> {
  await loginAs(
    page,
    process.env.TEST_ADMIN_EMAIL || 'admin@qpilot.ai',
    process.env.TEST_ADMIN_PASSWORD || 'qpilot123',
  )
}

// ── Screenshot helpers ────────────────────────────────────────────

/**
 * Take a named screenshot — called on test failure for debugging.
 */
export async function screenshotOnFailure(page: Page, testName: string): Promise<void> {
  await page.screenshot({
    path: `test-results/screenshots/${testName.replace(/\s+/g, '-')}.png`,
    fullPage: true,
  })
}
