"""
Handicap Scraper Module - Handles Handicaps.co.za scraping via Playwright
"""
import logging
import streamlit as st
from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)

# ================================================================================
# CACHE HELPERS
# ================================================================================
def get_cached_result(member_no):
    """Get cached scrape result"""
    return st.session_state.scrape_cache.get(member_no)

def save_cached_result(member_no, result):
    """Save scrape result to cache"""
    st.session_state.scrape_cache[member_no] = result

# ================================================================================
# PLAYWRIGHT LOGIN
# ================================================================================
def _login_and_wait_dashboard(page, username, password):
    """Login to Handicaps.co.za and wait for dashboard"""
    page.goto("https://www.handicaps.co.za/login", timeout=60000)
    page.wait_for_selector("#MemNo", timeout=15000)

    page.fill("#MemNo", username)
    page.fill("#Password", password)
    page.click("button.dg-login-signup__btn")

    page.wait_for_selector(
        "div.form-group.form-group-member.col-md-9",
        state="attached",
        timeout=60000,
    )

    page.wait_for_selector("#searchMemberName", state="attached", timeout=60000)
    page.wait_for_timeout(300)

def test_login(username, password):
    """Test login credentials"""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            _login_and_wait_dashboard(page, username, password)
            browser.close()
        return True
    except Exception as e:
        logger.error(f"Login failed: {e}")
        return False

# ================================================================================
# SCRAPE HANDICAP
# ================================================================================
def scrape_handicap_pw(username, password, membership_number, fallback_name=None):
    """Scrape handicap for a member"""
    cached = get_cached_result(membership_number)
    if cached:
        cached = cached.copy()
        cached["status"] = "cached"
        return cached

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            _login_and_wait_dashboard(page, username, password)

            page.fill("#searchMemberName", membership_number)
            page.wait_for_timeout(500)

            page.wait_for_selector("a[href*='golf-profile']", timeout=20000)
            page.wait_for_selector("span[data-bind*='HandicapIndexText']", timeout=20000)

            name = page.locator("a[href*='golf-profile']").first.inner_text().strip()

            if "," in name:
                parts = name.split(",")
                if len(parts) == 2:
                    name = parts[1].strip() + " " + parts[0].strip()

            index = page.locator(
                "span[data-bind*='HandicapIndexText']"
            ).first.inner_text().strip()

            browser.close()

            result = {
                "membership": membership_number,
                "name": name,
                "handicap_index": index,
                "cap": None,
                "status": "ok",
            }
            save_cached_result(membership_number, result)
            return result

    except Exception as e:
        logger.error(f"Scrape error for {membership_number}: {e}")
        result = {
            "membership": membership_number,
            "name": fallback_name,
            "handicap_index": None,
            "cap": None,
            "status": "error",
            "error": str(e),
        }
        save_cached_result(membership_number, result)
        return result
