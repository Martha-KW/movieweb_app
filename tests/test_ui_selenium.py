from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pytest


def test_add_movie(browser, test_client):
    test_client.post("/add_user", data={"username": "test_user"})
    # 1. Zur User-Seite navigieren (mit explizitem Wait)
    browser.get(f"http://localhost:5002/user/{test_user_id}")

    # 2. Sicherstellen, dass die Seite geladen ist
    WebDriverWait(browser, 5).until(
        EC.presence_of_element_located((By.TAG_NAME, "h1"))
    )

    # 3. Add-Button finden (mit PARTIAL_LINK_TEXT für Emoji-Toleranz)
    add_button = WebDriverWait(browser, 5).until(
        EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Add a New Movie"))
    )
    add_button.click()

    # 4. Formular ausfüllen
    WebDriverWait(browser, 5).until(
        EC.presence_of_element_located((By.NAME, "title"))
    ).send_keys("Inception (Test)")

    # Optionale Felder (falls OMDb nicht funktioniert)
    browser.find_element(By.NAME, "year").send_keys("2010")
    browser.find_element(By.NAME, "rating").send_keys("8.8")

    # 5. Formular absenden
    browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    # 6. Erfolg prüfen (über Flash-Nachricht oder Tabelleneintrag)
    try:
        WebDriverWait(browser, 5).until(
            EC.any_of(
                EC.text_to_be_present_in_element((By.CLASS_NAME, "flash-success"), "Movie"),
                EC.text_to_be_present_in_element((By.TAG_NAME, "td"), "Inception (Test)")
            )
        )
    except:
        pytest.fail("Movie was not added successfully")
