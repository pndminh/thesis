import { test, expect } from "@playwright/test";

test("test", async ({ page }) => {
  await page.goto("https://www.facebook.com/HcmIUcfs");
  await page.getByLabel("Close").click();
  await page
    .locator("span")
    .filter({ hasText: "#IU_AskAndAnswer 1. Mấy ac" })
    .getByRole("button")
    .click();
  await page
    .locator("span")
    .filter({ hasText: "#IU_AskAndAnswer 1. Em muốn" })
    .getByRole("button")
    .click();
  await page
    .locator("span")
    .filter({ hasText: "#IU_Tutor 1. Mình cần tìm gấp" })
    .getByRole("button")
    .click();
  await page
    .locator("span")
    .filter({ hasText: "#IU_Tutor 1. Mình cần tìm vài" })
    .getByRole("button")
    .click();
  await page
    .locator("span")
    .filter({ hasText: "#IU_Cfs11552 27/05/2024 20:51" })
    .getByRole("button")
    .click();
  await page
    .locator("span")
    .filter({ hasText: "#IU_Cfs11548 24/05/2024 8:24:" })
    .getByRole("button")
    .click();
  await page.getByText("trường ơi trường bị gì thế").click();
  await page.getByText("Em tham gia hiến máu ngay trê").click();
  await page
    .locator("span")
    .filter({ hasText: "#IU_Tutor1. Dạ em muốn tìm TA" })
    .getByRole("button")
    .click();
  await page
    .locator("span")
    .filter({ hasText: "#IU_Cfs11546 27/05/2024 18:29" })
    .getByRole("button")
    .click();
  await page
    .locator("span")
    .filter({ hasText: "#IU_Cfs1154328/05/2024 12:31:" })
    .getByRole("button")
    .click();
  await page
    .locator("span")
    .filter({ hasText: "#IU_AskAndAnswer1. Anh chị ơi" })
    .getByRole("button")
    .click();
  await page
    .locator("span")
    .filter({ hasText: "#IU_Cfs1154028/05/2024 15:11:" })
    .getByRole("button")
    .click();
});
