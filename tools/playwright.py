from playwright.async_api import async_playwright
from pydantic_ai import RunContext


async def fetch_job_content(ctx: RunContext, url: str) -> str:
    """
    MCP Tool: Navigates to a URL and extracts the main text content as Markdown.
    """
    print(f"   [Tool] 🕷️ Scraping {url}...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        try:
            await page.goto(url, timeout=30000)
            content = await page.content()
            print(f"   [Tool] ✅ Scraped content from {url}")
            with open("./scraped_content.html", "w", encoding="utf-8") as f:
                f.write(content)

            # Convert to Markdown to strip noise
            h = html2text.HTML2Text()
            h.ignore_links = True
            h.ignore_images = True
            h.body_width = 0
            return h.handle(content)[:20000]  # Limit context
        except Exception as e:
            return f"Error scraping: {e}"
        finally:
            await browser.close()
