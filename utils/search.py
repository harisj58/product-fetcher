import asyncio
from playwright.async_api import async_playwright
from agents.json_conformer import structure_json_data
import httpx
import os
import json

COUNTRY_LOCALE_MAPPING = {
    "AF",
    "AL",
    "DZ",
    "AS",
    "AD",
    "AO",
    "AI",
    "AQ",
    "AG",
    "AR",
    "AM",
    "AW",
    "AU",
    "AT",
    "AZ",
    "BS",
    "BH",
    "BD",
    "BB",
    "BY",
    "BE",
    "BZ",
    "BJ",
    "BM",
    "BT",
    "BO",
    "BA",
    "BW",
    "BV",
    "BR",
    "IO",
    "BN",
    "BG",
    "BF",
    "BI",
    "KH",
    "CM",
    "CA",
    "CV",
    "KY",
    "CF",
    "TD",
    "CL",
    "CN",
    "CX",
    "CC",
    "CO",
    "KM",
    "CG",
    "CD",
    "CK",
    "CR",
    "CI",
    "HR",
    "CU",
    "CY",
    "CZ",
    "DK",
    "DJ",
    "DM",
    "DO",
    "EC",
    "EG",
    "SV",
    "GQ",
    "ER",
    "EE",
    "ET",
    "FK",
    "FO",
    "FJ",
    "FI",
    "FR",
    "GF",
    "PF",
    "TF",
    "GA",
    "GM",
    "GE",
    "DE",
    "GH",
    "GI",
    "GR",
    "GL",
    "GD",
    "GP",
    "GU",
    "GT",
    "GG",
    "GN",
    "GW",
    "GY",
    "HT",
    "HM",
    "VA",
    "HN",
    "HK",
    "HU",
    "IS",
    "IN",
    "ID",
    "IR",
    "IQ",
    "IE",
    "IM",
    "IL",
    "IT",
    "JM",
    "JP",
    "JE",
    "JO",
    "KZ",
    "KE",
    "KI",
    "KP",
    "KR",
    "KW",
    "KG",
    "LA",
    "LV",
    "LB",
    "LS",
    "LR",
    "LY",
    "LI",
    "LT",
    "LU",
    "MO",
    "MK",
    "MG",
    "MW",
    "MY",
    "MV",
    "ML",
    "MT",
    "MH",
    "MQ",
    "MR",
    "MU",
    "YT",
    "MX",
    "FM",
    "MD",
    "MC",
    "MN",
    "ME",
    "MS",
    "MA",
    "MZ",
    "MM",
    "NA",
    "NR",
    "NP",
    "NL",
    "NC",
    "NZ",
    "NI",
    "NE",
    "NG",
    "NU",
    "NF",
    "MP",
    "NO",
    "OM",
    "PK",
    "PW",
    "PS",
    "PA",
    "PG",
    "PY",
    "PE",
    "PH",
    "PN",
    "PL",
    "PT",
    "PR",
    "QA",
    "RE",
    "RO",
    "RU",
    "RW",
    "SH",
    "KN",
    "LC",
    "PM",
    "VC",
    "WS",
    "SM",
    "ST",
    "SA",
    "SN",
    "RS",
    "SC",
    "SL",
    "SG",
    "SK",
    "SI",
    "SB",
    "SO",
    "ZA",
    "GS",
    "SS",
    "ES",
    "LK",
    "SD",
    "SR",
    "SJ",
    "SZ",
    "SE",
    "CH",
    "SY",
    "TW",
    "TJ",
    "TZ",
    "TH",
    "TL",
    "TG",
    "TK",
    "TO",
    "TT",
    "TN",
    "TR",
    "TM",
    "TC",
    "TV",
    "UG",
    "UA",
    "AE",
    "GB",
    "US",
    "UM",
    "UY",
    "UZ",
    "VU",
    "VE",
    "VN",
    "VG",
    "VI",
    "WF",
    "EH",
    "YE",
    "ZM",
    "ZW",
}


# Alternative approach with better error handling and retries
async def search_google(query: str, country: str):
    if country not in COUNTRY_LOCALE_MAPPING:
        print(f"Invalid country code: {country}")
        return {"status": "error", "message": "Invalid country code"}

    url = "https://serpapi.com/search"
    params = {
        "q": query,
        "engine": "bing_shopping",
        "cc": country.lower(),
        "api_key": os.environ.get("SERP_API_KEY"),
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        results = response.json()
        with open(f"./results.json", "w") as file:
            json.dump(results, file, indent=2)
        if "error" in results:
            return {"status": "error", "message": results["error"]}
    shopping_results = results.get("shopping_results", [])

    shopping_results = sorted(
        shopping_results, key=lambda x: x.get("extracted_price", float("inf"))
    )[:20]

    async with async_playwright() as playwright:
        chromium = playwright.chromium
        browser = await chromium.launch(headless=False)

        async def process_single_result(result):
            """Process a single result with its own page context"""
            if "external_link" in result:
                return result

            link = result.get("link", "")
            if not link:
                return result

            page = await browser.new_page()

            try:
                # Set longer timeout and better error handling
                await page.goto(link, wait_until="load", timeout=60000)

                # Extract external link
                try:
                    await page.wait_for_selector("a.br-oboSnOptLink", timeout=10000)
                    external_link = await page.locator(
                        "a.br-oboSnOptLink"
                    ).first.get_attribute("href")
                    result["external_link"] = external_link
                except Exception as e:
                    print(f"External link not found for {link}: {e}")
                    result["external_link"] = None
                    return result

                # Visit external link if available
                if result["external_link"]:
                    try:
                        await page.goto(
                            result["external_link"],
                            wait_until="load",
                            timeout=60000,
                        )
                        result["external_link"] = page.url  # Update with final URL

                        # Extract meta tags with better error handling
                        try:
                            await page.wait_for_selector("head")
                            meta_html = await page.evaluate(
                                """
                                () => {
                                    const metas = document.querySelectorAll('head meta');
                                    return Array.from(metas).map(meta => meta.outerHTML);
                                }
                            """
                            )
                            result["meta"] = "\n".join(meta_html) if meta_html else None
                        except Exception as meta_error:
                            print(f"Error extracting meta tags: {meta_error}")
                            result["meta"] = None

                    except Exception as ext_error:
                        print(
                            f"Error visiting external link {result['external_link']}: {ext_error}"
                        )
                        result["meta"] = None

            except Exception as e:
                print(f"Error processing {link}: {e}")
                result["external_link"] = None
                result["meta"] = None

            finally:
                await page.close()

            return result

        # Process results with concurrency control
        semaphore = asyncio.Semaphore(3)  # Limit concurrent pages

        async def process_with_semaphore(result):
            async with semaphore:
                return await process_single_result(result)

        # Process all results concurrently but with limits
        processed_results = await asyncio.gather(
            *[process_with_semaphore(result) for result in shopping_results],
            return_exceptions=True,
        )

        # Filter out any exceptions and keep valid results
        shopping_results = [
            result for result in processed_results if not isinstance(result, Exception)
        ]

        await browser.close()

    structured_results = await structure_json_data(shopping_results)
    return structured_results
