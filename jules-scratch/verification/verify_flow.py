from playwright.sync_api import sync_playwright, expect
import time
import random

def run_verification(playwright):
    """
    This script verifies the entire user registration and store creation flow.
    """
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    base_url = "http://127.0.0.1:5000"

    # Generate a unique username for each run
    unique_username = f"testuser_{int(time.time())}{random.randint(100, 999)}"
    password = "password123"

    try:
        # 1. Register a new user
        print(f"--- Step 1: Registering new user '{unique_username}' ---")
        page.goto(f"{base_url}/auth/kayit")
        expect(page.get_by_role("heading", name="Yeni Hesap Oluştur")).to_be_visible()

        page.locator("#username").fill(unique_username)
        page.locator("#first_name").fill("Test")
        page.locator("#last_name").fill("User")
        page.locator("#password").type(password)
        page.locator("#confirm_password").fill(password)
        page.get_by_role("button", name="Kayıt Ol").click()
        print("Registration form submitted.")

        # Verify success message and wait briefly
        expect(page.get_by_text("Kayıt işleminiz başarıyla tamamlandı!")).to_be_visible()
        time.sleep(1)

        # 2. Log in with the new user
        print(f"--- Step 2: Logging in as '{unique_username}' ---")
        # The URL can be either /giris or /login, so we just check for the heading
        expect(page.get_by_role("heading", name="E-ticaret Simulator'a Giriş Yap")).to_be_visible()

        page.locator("#username").fill(unique_username)
        page.locator("#password").type(password)
        page.get_by_role("button", name="Giriş Yap").click()
        print("Login form submitted.")

        # 3. Verify redirection to store creation and take screenshot
        print("--- Step 3: Verifying redirection to store creation page ---")
        expect(page).to_have_url(f"{base_url}/store/magaza/olustur", timeout=10000)
        expect(page.get_by_role("heading", name="Kendi Mağazanı Oluştur ve Oyuna Başla!")).to_be_visible()

        print("Taking screenshot of the store creation page...")
        page.screenshot(path="jules-scratch/verification/01_create_store_page.png")
        print("Screenshot '01_create_store_page.png' saved.")

        # 4. Create a new store
        print("--- Step 4: Creating a new store ---")
        page.get_by_label("Mağaza Adı").fill("Jules'in Test Dükkanı")
        page.get_by_label("Logo URL").fill("https://picsum.photos/seed/jules/200")
        page.get_by_label("Slogan").fill("Kalite ve güven bir arada!")
        page.get_by_label("Satış Alanı").select_option("giyim")
        page.get_by_role("button", name="Oyuna Başla").click()
        print("Store creation form submitted.")

        # 5. Verify redirection to main page and take screenshot
        print("--- Step 5: Verifying redirection to the main page ---")
        expect(page).to_have_url(f"{base_url}/", timeout=10000)
        expect(page.get_by_role("heading", name="Hoş Geldiniz!")).to_be_visible()

        print("Taking screenshot of the final main page...")
        page.screenshot(path="jules-scratch/verification/02_main_page_after_store.png")
        print("Screenshot '02_main_page_after_store.png' saved.")

        print("\n✅ Verification successful!")

    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        error_path = "jules-scratch/verification/error.png"
        page.screenshot(path=error_path)
        print(f"Error screenshot saved to '{error_path}'")
        print("\n--- Page HTML Content at time of error ---")
        print(page.content())
        print("--- End HTML Content ---")
    finally:
        print("--- Tearing down test ---")
        browser.close()

with sync_playwright() as playwright:
    run_verification(playwright)
