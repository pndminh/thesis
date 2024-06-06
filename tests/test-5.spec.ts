import { test, expect } from '@playwright/test';

test('test', async ({ page }) => {
  await page.goto('https://www.facebook.com/HcmIUcfs');
  await page.getByLabel('Close').click();
  await page.locator('div').filter({ hasText: /^View more commentsLê Đảm Anh Hưngtrường mình nhiều tót tót cơ mà :\)\)8 m$/ }).getByRole('button').click();
  await page.goto('https://www.facebook.com/HcmIUcfs');
  await page.getByLabel('Close').click();
  await page.locator('div').filter({ hasText: /^View more commentsLê Đảm Anh Hưngtrường mình nhiều tót tót cơ mà :\)\)9 m$/ }).getByRole('button').click();
  await page.locator('.x1uvtmcs > .__fb-light-mode').click();
  await page.getByLabel('Close').click();
  await page.getByRole('button', { name: 'View all 4 replies' }).click();
  await page.getByLabel('IU Confessions\'s post').getByText('Thúy AnMình đã học ở IU được').click();
  await page.getByText('Nguyen Le Truc AnNếu 10 năm').click();
  await page.locator('div').filter({ hasText: /^Top fanDat NimQuay xe đi em còn chừa chỗ cho anh đậu xe bên A2 :\(\(19$/ }).first().click();
  await page.locator('div:nth-child(9) > div > div > .x169t7cy > div > .x1r8uery').click();
  await page.getByRole('button', { name: 'View all 5 replies' }).click();
  await page.getByLabel('Close').click();
  await page.locator('span').filter({ hasText: '#IU_Cfs1156401/06/2024 19:48:' }).getByRole('button').click();
  await page.locator('span').filter({ hasText: '#IU_Cfs11562 30/05/2024 22:36' }).getByRole('button').click();
  await page.locator('span').filter({ hasText: '#IU_MissingSO1. Mình xin info' }).getByRole('button').click();
  await page.locator('span').filter({ hasText: '#IU_Cfs11559 01/06/2024 20:38' }).getByRole('button').click();
});