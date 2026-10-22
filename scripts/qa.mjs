import { createRequire } from 'node:module'
import { mkdirSync, writeFileSync } from 'node:fs'
import { resolve } from 'node:path'

const require = createRequire(import.meta.url)
const { chromium } = require('C:\\Users\\DELL\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\node\\node_modules\\playwright')
const outputDir = resolve('artifacts')
mkdirSync(outputDir, { recursive: true })

const browser = await chromium.launch({ headless: true, executablePath: 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe' })
const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 })
const consoleErrors = []
page.on('console', (message) => { if (message.type() === 'error') consoleErrors.push(message.text()) })
page.on('pageerror', (error) => consoleErrors.push(error.message))

await page.goto('http://127.0.0.1:5173/login', { waitUntil: 'networkidle' })
await page.getByRole('button', { name: '进入演示账户' }).click()
await page.waitForURL('**/dashboard')

const routes = ['/dashboard', '/market', '/stock/SZ.000630', '/screener', '/radar', '/watchlist', '/alerts', '/portfolio', '/review', '/strategies', '/quant', '/backtest', '/settings']
const results = []

for (const route of routes) {
  await page.goto(`http://127.0.0.1:5173${route}`, { waitUntil: 'networkidle' })
  await page.waitForTimeout(350)
  const metrics = await page.evaluate(() => ({
    title: document.querySelector('h1')?.textContent?.trim() || '',
    scrollWidth: document.documentElement.scrollWidth,
    clientWidth: document.documentElement.clientWidth,
    bodyText: document.body.innerText.length,
    charts: document.querySelectorAll('canvas').length,
  }))
  results.push({ route, ...metrics, horizontalOverflow: metrics.scrollWidth > metrics.clientWidth + 2 })
}

await page.goto('http://127.0.0.1:5173/dashboard', { waitUntil: 'networkidle' })
await page.screenshot({ path: resolve(outputDir, 'qa-dashboard.png'), fullPage: true })
await page.locator('.global-search input').fill('铜陵')
await page.getByRole('button', { name: /铜陵有色/ }).click()
await page.waitForURL('**/stock/SZ.000630')
await page.waitForTimeout(500)
await page.screenshot({ path: resolve(outputDir, 'qa-stock-detail.png'), fullPage: true })

await page.goto('http://127.0.0.1:5173/screener', { waitUntil: 'networkidle' })
await page.getByRole('button', { name: /低位放量/ }).last().click()
await page.waitForTimeout(500)
await page.screenshot({ path: resolve(outputDir, 'qa-screener.png'), fullPage: true })

await page.goto('http://127.0.0.1:5173/watchlist', { waitUntil: 'networkidle' })
await page.locator('tbody tr').first().click()
const watchDrawerVisible = await page.locator('.el-drawer').isVisible()
await page.keyboard.press('Escape')

await page.goto('http://127.0.0.1:5173/alerts', { waitUntil: 'networkidle' })
await page.locator('.el-switch').first().click()
const alertToggleWorked = !(await page.locator('.el-switch').first().getAttribute('class'))?.includes('is-checked')

await page.goto('http://127.0.0.1:5173/portfolio', { waitUntil: 'networkidle' })
await page.getByRole('button', { name: '交易记录' }).click()
const transactionTabVisible = await page.getByText('2026-08-28').isVisible()

await page.goto('http://127.0.0.1:5173/backtest', { waitUntil: 'networkidle' })
await page.getByRole('button', { name: /运行 Demo 回测/ }).click()
await page.waitForTimeout(900)
const backtestVisible = await page.getByText('总信号数').isVisible()

await page.goto('http://127.0.0.1:5173/quant', { waitUntil: 'networkidle' })
await page.waitForTimeout(500)
await page.screenshot({ path: resolve(outputDir, 'qa-quant-lab.png'), fullPage: true })
await page.locator('.quant-tabs button').filter({ hasText: '订单' }).click()
const quantOrdersVisible = await page.getByText('Paper Orders').isVisible()
await page.getByRole('button', { name: '撤销', exact: true }).first().click()
const quantCancelWorked = await page.getByText('CANCELLED').isVisible()
await page.getByRole('button', { name: '运行日志', exact: true }).click()
await page.getByRole('button', { name: 'RISK', exact: true }).click()
const quantLogFilterWorked = await page.getByText('风险检查通过').first().isVisible()
await page.getByRole('button', { name: '新建模拟', exact: true }).click()
await page.locator('.config-grid input').nth(0).fill('10万趋势测试账户')
await page.locator('.config-grid input').nth(1).fill('100000')
await page.getByRole('button', { name: '创建虚拟实例', exact: true }).click()
const quantInstanceCreated = await page.getByText('10万趋势测试账户').first().isVisible()
await page.getByRole('button', { name: '启动模拟', exact: true }).first().click()
const quantStarted = await page.getByText('运行中', { exact: true }).first().isVisible()
await page.getByRole('button', { name: '暂停', exact: true }).first().click()
const quantPaused = await page.getByText('已暂停', { exact: true }).first().isVisible()

await page.setViewportSize({ width: 1200, height: 820 })
const compactResults = []
for (const route of ['/dashboard', '/market', '/stock/SZ.000630', '/screener', '/portfolio', '/quant']) {
  await page.goto(`http://127.0.0.1:5173${route}`, { waitUntil: 'networkidle' })
  const metrics = await page.evaluate(() => ({ scrollWidth: document.documentElement.scrollWidth, clientWidth: document.documentElement.clientWidth }))
  compactResults.push({ route, ...metrics, horizontalOverflow: metrics.scrollWidth > metrics.clientWidth + 2 })
}

const interactions = { searchOpenedStock: true, screenerPresetRan: true, watchDrawerVisible, alertToggleWorked, transactionTabVisible, backtestVisible, quantOrdersVisible, quantCancelWorked, quantLogFilterWorked, quantInstanceCreated, quantStarted, quantPaused }
writeFileSync(resolve(outputDir, 'qa-results.json'), JSON.stringify({ routes: results, compactResults, consoleErrors, interactions }, null, 2))
await browser.close()

console.log(JSON.stringify({ routes: results, compactResults, consoleErrors, interactions }, null, 2))
