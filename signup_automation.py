import asyncio
import os
import re
import sys
import time
import random
import string
from playwright.async_api import async_playwright

# Force unbuffered output so every line appears immediately
sys.stdout.reconfigure(line_buffering=True)

# CONFIGURATION
BASE_URL = "https://authorized-partner.vercel.app"
TS       = int(time.time())

# -- Random data pools --
_FIRST_NAMES = [
    "Aarav", "Bishal", "Carlos", "David", "Elena", "Fatima", "Gaurav",
    "Hiroshi", "Isabelle", "Jiang", "Kumar", "Liam", "Manisha", "Nora",
    "Oscar", "Priya", "Qasim", "Rashid", "Sara", "Tenzin", "Uma",
    "Viktor", "Wei", "Xena", "Yuki", "Zara",
]
_LAST_NAMES = [
    "Adhikari", "Bhandari", "Chen", "Diaz", "Evans", "Fernandez",
    "Gurung", "Hayashi", "Ibrahim", "Joshi", "Kim", "Lamichhane",
    "Maharjan", "Nakamura", "Olsen", "Patel", "Quinn", "Rai",
    "Sharma", "Thapa", "Upadhyay", "Vaidya", "Wang", "Xu", "Yamada", "Zhang",
]
_ROLES = [
    "Managing Director", "Chief Executive Officer", "Operations Manager",
    "Senior Consultant", "Branch Manager", "Head of Admissions",
    "Country Director", "Regional Manager", "Partner", "Founder",
]
_AGENCY_PREFIXES = [
    "Global", "Elite", "Prime", "Apex", "Pacific", "Summit",
    "Prestige", "Pioneer", "Horizon", "Zenith", "Vertex", "Nova",
]
_AGENCY_SUFFIXES = [
    "Education Consultancy", "Study Abroad", "International Services",
    "Edu Solutions", "Academic Partners", "Learning Hub",
    "Migration Services", "Career Pathways", "Consulting Group",
]
_DOMAINS = [
    "educonsult", "studypath", "globaleduhub", "primeadvisors",
    "elitestudies", "apexedu", "horizonlearn", "summitcareers",
]
_STREETS = [
    "Durbar Marg", "New Road", "Lazimpat", "Thamel Chowk",
    "Putalisadak", "Battisputali", "Baluwatar", "Kamaladi",
]
_CITIES = [
    "Kathmandu", "Lalitpur", "Bhaktapur",
    "Pokhara", "Biratnagar", "Chitwan",
]
_ALL_REGIONS = [
    "Australia", "Europe", "North America", "Asia", "Middle East",
    "United Kingdom", "South America", "Africa",
]
_EXP_OPTIONS = ["1 Year", "2 Years", "3 Years", "5 Years", "10 Years"]
_FOCUS_AREAS = [
    "University admissions consulting and student visa processing",
    "Scholarship guidance and academic pathway planning",
    "Postgraduate placement and research program advisory",
    "Vocational training enrollment and skills-based migration",
    "Language course placement and pre-departure orientation",
    "Medical and engineering university admissions",
    "MBA and business school application management",
]
_CERT_OPTIONS = [
    "ICEF Certified Education Agent",
    "PIER Certified",
    "QEAC Registered Agent",
    "British Council Partner",
    "AIRC Certified",
    "NAFSA Member",
    "Education New Zealand Recognised Agent",
]
_ALL_COUNTRIES = [
    "Australia", "Canada", "United Kingdom", "United States",
    "New Zealand", "Germany", "Japan", "South Korea",
]
_ALL_SERVICES = [
    "Career Counseling",
    "Admission Applications",
    "Visa Processing",
    "Test Preparation",
]

def _rand_password(length=14):
    """Generate a strong random password meeting common complexity rules."""
    upper = random.choice(string.ascii_uppercase)
    lower = random.choice(string.ascii_lowercase)
    digit = random.choice(string.digits)
    symbol = random.choice("!@#$%&*")
    rest = ''.join(random.choices(
        string.ascii_letters + string.digits + "!@#$%&*", k=length - 4
    ))
    pwd = list(upper + lower + digit + symbol + rest)
    random.shuffle(pwd)
    return ''.join(pwd)

# Account (Step 1)
EMAIL_USER   = f"autobot{TS}"
EMAIL        = f"{EMAIL_USER}@mailinator.com"
FIRST_NAME   = random.choice(_FIRST_NAMES)
LAST_NAME    = random.choice(_LAST_NAMES)
PHONE        = f"9841{random.randint(100000, 999999)}"   # Nepal mobile
PASSWORD     = _rand_password()

# -- Agency Details (Step 2) --
AGENCY_NAME  = f"{random.choice(_AGENCY_PREFIXES)} {random.choice(_AGENCY_SUFFIXES)} {TS}"
ROLE         = random.choice(_ROLES)
AGENCY_EMAIL = f"agency{TS}@mailinator.com"
AGENCY_WEB   = f"www.{random.choice(_DOMAINS)}{random.randint(10,99)}.com"
AGENCY_ADDR  = f"{random.choice(_STREETS)}, {random.choice(_CITIES)}, Nepal"
REGIONS      = random.sample(_ALL_REGIONS, k=random.randint(1, 3))

# -- Professional Experience (Step 3) --
EXP_YEARS      = random.choice(_EXP_OPTIONS)
STUDENTS_PA    = str(random.randint(20, 500))
FOCUS_AREA     = random.choice(_FOCUS_AREAS)
SUCCESS_METRIC = str(random.randint(70, 99))
SERVICES       = random.sample(_ALL_SERVICES, k=random.randint(2, len(_ALL_SERVICES)))

# -- Verification & Preferences (Step 4) --
BIZ_REG_NO     = f"BRN-{TS}"
PREF_COUNTRIES = random.sample(_ALL_COUNTRIES, k=random.randint(1, 3))
INST_TYPES     = ["Universities", "Colleges"]
CERT_DETAILS   = ", ".join(random.sample(_CERT_OPTIONS, k=random.randint(2, 4)))

# HELPERS
BAR = 64


def banner(step, title):
    """Print a highly visible step header."""
    print(f"\n{'=' * BAR}")
    print(f"  STEP {step}  --  {title}")
    print(f"{'=' * BAR}")


def ok(msg):
    print(f"  [ OK ]  {msg}")


def info(msg):
    print(f"  [INFO]  {msg}")


def warn(msg):
    print(f"  [WARN]  {msg}")


# OTP retrieval from Mailinator
async def fetch_otp(browser, user, retries=20, interval=3):
    """Open a disposable browser context, scrape the OTP from Mailinator."""
    inbox_url = f"https://www.mailinator.com/v4/public/inboxes.jsp?to={user}"
    ctx = await browser.new_context()
    pg  = await ctx.new_page()
    otp = None

    for attempt in range(1, retries + 1):
        try:
            await pg.goto(inbox_url, wait_until="networkidle", timeout=20_000)
            await pg.wait_for_timeout(2000)

            rows = pg.locator("table tbody tr")
            count = await rows.count()

            # Row 0 is the header ("From  Subject  Received")
            # Real emails start at row 1
            if count < 2:
                info(f"Attempt {attempt}/{retries}: inbox empty ({count} rows) — retrying in {interval}s …")
                await pg.wait_for_timeout(interval * 1000)
                continue

            # Find the actual email row (skip header at index 0)
            email_row = None
            for i in range(1, count):
                row_text = await rows.nth(i).inner_text()
                info(f"  Row {i}: {row_text[:100]}")
                if any(kw in row_text.lower() for kw in ["otp", "signup", "verif", "confirm", "code"]):
                    email_row = rows.nth(i)
                    break

            if email_row is None:
                email_row = rows.nth(1)  # fallback: first non-header row

            info("Opening email message …")
            await email_row.click()
            await pg.wait_for_timeout(5000)

            # Extract OTP from the email iframe
            body = ""
            try:
                body = await (
                    pg.frame_locator("#html_msg_body")
                      .locator("body")
                      .inner_text(timeout=10_000)
                )
                info(f"  iframe body (first 200): {body[:200]}")
            except Exception as e:
                warn(f"  Could not read iframe: {e}")

            if not body:
                # Fallback: check all frames
                for frame in pg.frames:
                    try:
                        txt = await frame.locator("body").inner_text(timeout=3000)
                        if "otp" in txt.lower() or "verif" in txt.lower() or "code" in txt.lower():
                            body = txt
                            break
                    except:
                        continue

            if body:
                m = re.search(r"\b(\d{6})\b", body)
                if m:
                    otp = m.group(1)
                    ok(f"OTP retrieved: {otp}")
                    break
                else:
                    warn(f"Attempt {attempt}: email body found but no 6-digit OTP")
            else:
                warn(f"Attempt {attempt}: email clicked but body is empty")

        except Exception as exc:
            info(f"Attempt {attempt}: {str(exc)[:100]}")

        await pg.wait_for_timeout(interval * 1000)

    await ctx.close()
    if otp is None:
        raise RuntimeError("Could not retrieve OTP after maximum retries — aborting.")
    return otp


# Discover available options from a dialog-combobox 
async def discover_dialog_options(page, combo_locator):
    """Open a dialog-combobox, read all available option texts, close it."""
    await combo_locator.click()
    await page.wait_for_timeout(1000)

    dlg = page.locator("[role='dialog']")
    await dlg.wait_for(state="visible", timeout=5000)

    available = []
    spans = dlg.locator("div[role='option'] span, label span, [data-value] span, span")
    count = await spans.count()
    for i in range(count):
        txt = (await spans.nth(i).inner_text()).strip()
        if txt and txt not in available and len(txt) > 1:
            available.append(txt)

    await page.keyboard.press("Escape")
    await page.wait_for_timeout(500)
    return available


# Discover available options from a standard dropdown
async def discover_dropdown_options(page, combo_locator):
    """Open a Radix select dropdown, read all role='option' texts, close it."""
    await combo_locator.click()
    await page.wait_for_timeout(1000)

    available = []
    opts = page.locator("[role='option']")
    count = await opts.count()
    for i in range(count):
        txt = (await opts.nth(i).inner_text()).strip()
        if txt and txt not in available:
            available.append(txt)

    await page.keyboard.press("Escape")
    await page.wait_for_timeout(500)
    return available


# Discover available checkbox labels
async def discover_checkbox_labels(page):
    """Read all label texts that have an adjacent checkbox button."""
    available = []
    labels = page.locator("label")
    count = await labels.count()
    for i in range(count):
        parent = labels.nth(i).locator("..")
        btn = parent.locator("button[role='checkbox']")
        if await btn.count() > 0:
            txt = (await labels.nth(i).inner_text()).strip()
            if txt:
                available.append(txt)
    return available


# Dialog-based multi-select combobox (Region / Country)
async def pick_from_dialog_combobox(page, combo_locator, options):
    """Click a Radix dialog-combobox, tick the desired options, press Escape."""
    await combo_locator.click()
    await page.wait_for_timeout(1000)

    dlg = page.locator("[role='dialog']")
    await dlg.wait_for(state="visible", timeout=5000)

    for opt in options:
        el = dlg.locator(f"span:text-is('{opt}')")
        if await el.count() == 0:                       # fallback: partial text
            el = dlg.get_by_text(opt, exact=False)
        if await el.count() > 0:
            await el.first.click()
            ok(f"    [x] {opt}")
            await page.wait_for_timeout(300)
        else:
            warn(f"    option '{opt}' not found in dialog")

    await page.keyboard.press("Escape")
    await page.wait_for_timeout(500)


# Tick checkbox buttons next to labels 
async def tick_checkboxes(page, labels):
    for txt in labels:
        lbl = page.locator(f"label:has-text('{txt}')").first
        if await lbl.count() == 0:
            warn(f"    checkbox '{txt}' not found")
            continue
        parent = lbl.locator("..")
        btn = parent.locator("button[role='checkbox']")
        if await btn.count() > 0:
            await btn.click()
        else:
            await lbl.click()
        ok(f"    [x] {txt}")
        await page.wait_for_timeout(300)


# MAIN
async def main():
    print(f"\n{'=' * BAR}")
    print(f"AUTOMATED SIGNUP — authorized-partner.vercel.app")
    print(f"{'=' * BAR}")
    print(f"  Email     : {EMAIL}")
    print(f"  Phone     : +977 {PHONE}")
    print(f"  Agency    : {AGENCY_NAME}")
    print(f"  Password  : {PASSWORD}")

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False, slow_mo=200)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 900}
        )
        page = await context.new_page()

        # STEP 0 : Terms
        banner(0, "TERMS & CONDITIONS")

        info(f"Navigating to {BASE_URL} …")
        await page.goto(BASE_URL,
                        wait_until="networkidle", timeout=30_000)
        await page.wait_for_timeout(2000)

        # Discover a visible registration link from the homepage UI
        info("Scanning page for visible registration links …")
        all_links = page.locator("a[href]")
        link_count = await all_links.count()
        candidates = []
        for i in range(link_count):
            link = all_links.nth(i)
            href = await link.get_attribute("href")
            if href and "register" in href:
                if await link.is_visible():
                    label = (await link.inner_text()).strip()
                    box = await link.bounding_box()
                    info(f"  Visible link #{len(candidates)}: '{label}' → {href}  (y={box['y']:.0f})" if box else f"  Visible link: '{label}' → {href}")
                    candidates.append((link, label, box))
        if not candidates:
            raise RuntimeError("Could not discover a visible registration link on the homepage.")

        reg_link, reg_label, _ = candidates[0]
        for link, label, box in candidates:
            if box and box["y"] > 100:  # skip navbar links at the top
                reg_link, reg_label = link, label
                break

        info(f"Clicking: '{reg_label}'")
        await reg_link.scroll_into_view_if_needed()
        await page.wait_for_timeout(1000)
        
        await reg_link.hover()

        await reg_link.click()
        ok(f"Clicked '{reg_label}'")
        await page.wait_for_timeout(3000)

        await page.locator("button[role='checkbox']").click()
        ok("Agreed to Terms & Conditions")

        await page.locator("button:has-text('Continue')").click()
        ok("Clicked Continue")
        await page.wait_for_timeout(2000)

        # STEP 1 : Account Setup
        banner(1, "ACCOUNT SETUP")

        fields_1 = {
            "firstName":       FIRST_NAME,
            "lastName":        LAST_NAME,
            "email":           EMAIL,
            "phoneNumber":     PHONE,
            "password":        PASSWORD,
            "confirmPassword": PASSWORD,
        }
        for name, val in fields_1.items():
            await page.fill(f"input[name='{name}']", val)
            ok(f"{name:>20s} = {val}")

        await page.locator("button[type='submit']").click()
        ok("Account form submitted — waiting for OTP screen …")

        otp_input = page.locator("input[inputmode='numeric']")
        await otp_input.wait_for(state="visible", timeout=30_000)
        ok("OTP input field appeared")

        # STEP 1b : OTP Verification
        banner("1b", "OTP VERIFICATION  (via Mailinator)")

        MAX_OTP_ATTEMPTS = 3
        otp_verified = False

        for otp_attempt in range(1, MAX_OTP_ATTEMPTS + 1):
            info(f"OTP attempt {otp_attempt}/{MAX_OTP_ATTEMPTS}")
            info("Waiting 5 s for email delivery …")
            await page.wait_for_timeout(5_000)

            otp = await fetch_otp(browser, EMAIL_USER)

            # Re-locate the OTP input (may have been re-rendered after resend)
            otp_input = page.locator("input[inputmode='numeric']")
            await otp_input.first.wait_for(state="visible", timeout=10_000)

            # Clear any previously typed OTP digits
            otp_fields = page.locator("input[inputmode='numeric']")
            otp_count = await otp_fields.count()
            for idx in range(otp_count):
                await otp_fields.nth(idx).fill("")
            await page.wait_for_timeout(200)

            await otp_input.first.click()
            await page.wait_for_timeout(300)
            for digit in otp:
                await page.keyboard.press(digit)
                await page.wait_for_timeout(150)
            ok(f"Typed OTP: {otp}")

            await page.locator("button[type='submit']").click()
            ok("Verification submitted")
            await page.wait_for_timeout(4000)

            # Check for error messages on the page
            error_text = ""
            try:
                error_el = page.locator("[role='alert'], .text-red, .text-destructive, .error")
                if await error_el.count() > 0:
                    error_text = await error_el.first.inner_text(timeout=2000)
                    warn(f"Page error detected: {error_text}")
            except Exception:
                pass

            if "expired" in error_text.lower() or "invalid" in error_text.lower():
                if otp_attempt < MAX_OTP_ATTEMPTS:
                    info("OTP expired or invalid — attempting to resend …")
                    resend_btn = page.locator("button:has-text('Resend'), button:has-text('resend'), a:has-text('Resend'), a:has-text('resend')")
                    if await resend_btn.count() > 0:
                        await resend_btn.first.click()
                        ok("Clicked Resend OTP")
                        await page.wait_for_timeout(3000)
                    else:
                        warn("No resend button found — retrying fetch anyway")
                    continue
                else:
                    raise RuntimeError("OTP verification failed after all retry attempts.")
            else:
                otp_verified = True
                break

        if not otp_verified:
            raise RuntimeError("OTP verification did not succeed.")

        current_url = page.url
        info(f"Post-verification URL: {current_url}")

        # STEP 2 : Agency Details
        banner(2, "AGENCY DETAILS")

        await page.wait_for_selector(
            "input[name='agency_name']", state="visible", timeout=30_000
        )

        fields_2 = {
            "agency_name":    AGENCY_NAME,
            "role_in_agency": ROLE,
            "agency_email":   AGENCY_EMAIL,
            "agency_website": AGENCY_WEB,
            "agency_address": AGENCY_ADDR,
        }
        for name, val in fields_2.items():
            await page.fill(f"input[name='{name}']", val)
            ok(f"{name:>20s} = {val}")

        info("Discovering available Regions of Operation …")
        region_combo = page.locator("button[role='combobox']")
        available_regions = await discover_dialog_options(page, region_combo)
        info(f"Available regions: {available_regions}")
        if available_regions:
            pick_count = random.randint(1, min(3, len(available_regions)))
            chosen_regions = random.sample(available_regions, k=pick_count)
        else:
            chosen_regions = REGIONS  # fallback to config
        info(f"Selected regions: {chosen_regions}")
        await pick_from_dialog_combobox(page, region_combo, chosen_regions)

        await page.locator("button[type='submit']").click()
        ok("Agency details submitted")
        await page.wait_for_timeout(5000)

        # STEP 3 : Professional Experience 
        banner(3, "PROFESSIONAL EXPERIENCE")

        # Years of Experience — discover then pick
        info("Discovering Years of Experience options …")
        exp_combo = page.locator("button[role='combobox']").first
        available_years = await discover_dropdown_options(page, exp_combo)
        info(f"Available experience options: {available_years}")
        if available_years:
            chosen_exp = random.choice(available_years)
        else:
            chosen_exp = EXP_YEARS  # fallback
        info(f"Selecting: {chosen_exp}")
        await exp_combo.click()
        await page.wait_for_timeout(1000)
        year_opt = page.locator(f"[role='option']:has-text('{chosen_exp}')")
        if await year_opt.count() > 0:
            await year_opt.first.click()
        else:
            await page.get_by_text(chosen_exp, exact=False).first.click()
        ok(f"Years of Experience = {chosen_exp}")
        await page.wait_for_timeout(500)

        fields_3 = {
            "number_of_students_recruited_annually": STUDENTS_PA,
            "focus_area":    FOCUS_AREA,
            "success_metrics": SUCCESS_METRIC,
        }
        for name, val in fields_3.items():
            await page.fill(f"input[name='{name}']", val)
            ok(f"{name:>42s} = {val}")

        info("Discovering available services …")
        available_services = await discover_checkbox_labels(page)
        info(f"Available services: {available_services}")
        if available_services:
            pick_count = random.randint(2, len(available_services))
            chosen_services = random.sample(available_services, k=pick_count)
        else:
            chosen_services = SERVICES  # fallback
        info(f"Selected services: {chosen_services}")
        await tick_checkboxes(page, chosen_services)

        await page.locator("button[type='submit']").click()
        ok("Professional experience submitted")
        await page.wait_for_timeout(5000)

        # STEP 4 : Verification 
        banner(4, "VERIFICATION & PREFERENCES")

        await page.wait_for_selector(
            "input[name='business_registration_number']",
            state="visible", timeout=15_000,
        )

        await page.fill(
            "input[name='business_registration_number']", BIZ_REG_NO
        )
        ok(f"business_registration_number = {BIZ_REG_NO}")

        info("Discovering available Preferred Countries …")
        country_combo = page.locator("button[role='combobox']")
        available_countries = await discover_dialog_options(page, country_combo)
        info(f"Available countries: {available_countries}")
        if available_countries:
            pick_count = random.randint(1, min(3, len(available_countries)))
            chosen_countries = random.sample(available_countries, k=pick_count)
        else:
            chosen_countries = PREF_COUNTRIES  # fallback
        info(f"Selected countries: {chosen_countries}")
        await pick_from_dialog_combobox(page, country_combo, chosen_countries)

        info("Discovering available Institution Types …")
        available_inst = await discover_checkbox_labels(page)
        info(f"Available institution types: {available_inst}")
        if available_inst:
            pick_count = random.randint(1, len(available_inst))
            chosen_inst = random.sample(available_inst, k=pick_count)
        else:
            chosen_inst = INST_TYPES  # fallback
        info(f"Selected institution types: {chosen_inst}")
        await tick_checkboxes(page, chosen_inst)

        await page.fill("input[name='certification_details']", CERT_DETAILS)
        ok(f"certification_details = {CERT_DETAILS}")

        # File uploads 
        info("Uploading business documents …")
        doc_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "_temp_business_doc.txt",
        )
        with open(doc_path, "w") as fh:
            fh.write(
                f"Business Registration Document\n"
                f"Agency: {AGENCY_NAME}\n"
                f"Registration No: {BIZ_REG_NO}\n"
                f"Date: {time.strftime('%Y-%m-%d')}\n"
            )

        file_inputs = page.locator("input[type='file']")
        n = await file_inputs.count()
        for i in range(n):
            await file_inputs.nth(i).set_input_files(doc_path)
            ok(f"    file input #{i + 1} ← _temp_business_doc.txt")
            await page.wait_for_timeout(500)

        add_docs = page.locator("button:has-text('Add Documents')")
        if await add_docs.count() > 0 and await add_docs.is_visible():
            await add_docs.click()
            ok("Clicked 'Add Documents'")
            await page.wait_for_timeout(1000)

        # Final Submit
        submit = page.locator("button[type='submit']:has-text('Submit')")
        if await submit.count() == 0:
            submit = page.locator("button[type='submit']").last
        await submit.click()
        ok("FINAL SUBMIT clicked — Signup complete!")
        await page.wait_for_timeout(5000)

        # RESULT 
        final_url = page.url
        body = await page.locator("body").inner_text()

        print(f"\n{'═' * BAR}")
        print(f"#  SIGNUP AUTOMATION FINISHED  (SUCCESS)")
        print(f"{'═' * BAR}")
        print(f"  Final URL : {final_url}")
        print(f"  Page content (first lines):")
        for line in body.strip().splitlines()[:10]:
            stripped = line.strip()
            if stripped:
                print(f"    │ {stripped}")

        # Cleanup temp file
        try:
            os.remove(doc_path)
        except OSError:
            pass

        await page.wait_for_timeout(7_000)

        await context.close()
        await browser.close()

    print(f"\n{'═' * BAR}")
    print("  Done. All resources released.")
    print(f"{'═' * BAR}\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as exc:
        import traceback
        print(f"\n!!! ERROR !!!\n{exc}")
        traceback.print_exc()
