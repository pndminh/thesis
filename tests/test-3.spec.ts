import { test, expect } from "@playwright/test";

test("test", async ({ page }) => {
  await page.goto("https://www.facebook.com/HcmIUcfs");
  await page
    .getByRole("textbox", { name: "Email address or phone number" })
    .click();
  await page
    .getByRole("textbox", { name: "Email address or phone number" })
    .fill("dong");
  await page
    .getByRole("textbox", { name: "Email address or phone number" })
    .click({
      clickCount: 3,
    });
  await page
    .getByRole("textbox", { name: "Email address or phone number" })
    .fill("dongminh1510@gmail.com");
  await page
    .locator("#login_popup_cta_form")
    .getByRole("textbox", { name: "Password" })
    .click();
  await page
    .locator("#login_popup_cta_form")
    .getByRole("textbox", { name: "Password" })
    .fill("toinfinityandbeyond22222");
  await page
    .locator("#login_popup_cta_form")
    .getByLabel("Accessible login button")
    .click();
  await page
    .locator("span")
    .filter({ hasText: "#IU_Cfs11562 30/05/2024 22:36" })
    .getByRole("button")
    .click();
  await page
    .locator("span")
    .filter({ hasText: "#IU_Cfs11561 22/05/2024 18:00" })
    .getByRole("button")
    .click();
  await page.getByText("3… See more").click();
  await page.getByText("3… See more").click();
  await page
    .locator("span")
    .filter({ hasText: "#IU_MissingSO1. Mình xin info" })
    .getByRole("button")
    .click();
  await page.getByText("Em nghe nói chỉ có 30% SV IU").click();
  await page
    .locator("span")
    .filter({ hasText: "#IU_Cfs11559 01/06/2024 20:38" })
    .getByRole("button")
    .click();
  await page
    .locator("span")
    .filter({ hasText: "#IU_Cfs11558Mình là người đã" })
    .getByRole("button")
    .click();
  await page
    .locator("span")
    .filter({ hasText: "#IU_Cfs11555 27/05/2024 20:54" })
    .getByRole("button")
    .click();
  await page
    .locator("span")
    .filter({ hasText: "#IU_Cfs11553 28/05/2024 15:31" })
    .getByRole("button")
    .click();
  await page
    .locator(
      "div:nth-child(7) > .x1yztbdb > div > div > div > div > div > div > div > div > div > div:nth-child(13) > div > div"
    )
    .click();
});
