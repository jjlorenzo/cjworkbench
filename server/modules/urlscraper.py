import aiohttp
import asyncio
import re
from django.conf import settings
from django.utils import timezone
import pandas as pd
from .moduleimpl import ModuleImpl
from .types import ProcessResult


async def async_get_url(row, url):
    """
    Return a Future (row, status, text).

    The Future will resolve within settings.SCRAPER_TIMEOUT seconds. `status`
    may be '

    The Future will resolve within settings.SCRAPER_TIMEOUT seconds. The
    exception may be `asyncio.TimeoutError`, `ValueError` (invalid URL) or
    `aiohttp.client_exceptions.ClientError`.
    """
    session = aiohttp.ClientSession()

    try:
        response = await session.get(url, timeout=settings.SCRAPER_TIMEOUT)
        # We have the header. Now read the content.
        # response.text() times out according to SCRAPER_TIMEOUT above. See
        # https://docs.aiohttp.org/en/stable/client_quickstart.html#timeouts
        text = await response.text()

        return (row, str(response.status), text)
    except asyncio.TimeoutError:
        return (row, 'Timed out', '')
    except aiohttp.InvalidURL:
        return (row, 'Invalid URL', '')
    except aiohttp.ClientError as err:
        return (row, f"Can't connect: {err}", '')
    except Exception as err:
        return (row, f'Unknown error: {err}', '')


# Asynchronously scrape many urls, and store the results in the table
async def scrape_urls(urls, result_table):
    next_queued_row = 0  # index into urls
    fetching = set()  # {Future<response>}

    max_fetchers = settings.SCRAPER_NUM_CONNECTIONS

    while next_queued_row < len(urls) or fetching:
        # start tasks until we max out connections, or run out of urls
        while next_queued_row < len(urls) and len(fetching) < max_fetchers:
            row = next_queued_row
            url = urls[row].strip()
            fetching.add(async_get_url(row, url))

            next_queued_row += 1

        assert fetching

        # finish one or more tasks, then loop
        done, pending = await asyncio.wait(fetching,
                                           return_when=asyncio.FIRST_COMPLETED)

        for task in done:
            row, status, text = await task
            result_table.loc[row, 'status'] = status
            result_table.loc[row, 'html'] = text

        fetching = pending  # delete done tasks


class URLScraper(ModuleImpl):
    @staticmethod
    def render(params, table, *, fetch_result, **kwargs):
        urlsource = params.get_param_menu_string('urlsource')
        if urlsource == 'Input column':
            urlcol = params.get_param_column('urlcol', table)
            if not urlcol:
                return table  # input not specified
        else:
            urllist = params.get_param_string('urllist')
            if not urllist:
                return table  # input not specified

        return fetch_result

    # Scrapy scrapy scrapy
    @staticmethod
    async def fetch(wfm):
        urls = []
        params = wfm.get_params()
        urlsource = params.get_param_menu_string('urlsource')

        if urlsource == 'List':
            urllist_text = params.get_param_string('urllist')
            urllist_raw = urllist_text.split('\n')
            for url in urllist_raw:
                s_url = url.strip()
                if len(s_url) == 0:
                    continue
                # Fix in case user adds an URL without http(s) prefix
                if not re.match('^https?://.*', s_url):
                    urls.append('http://{}'.format(s_url))
                else:
                    urls.append(s_url)
        elif urlsource == 'Input column':
            # We won't execute here -- there's no need: the user clicked a
            # button so should be pretty clear on what the input is.
            input_cache = wfm.previous_in_stack().get_cached_render_result()
            if input_cache:
                prev_table = input_cache.result.dataframe
            else:
                prev_table = pd.DataFrame()

            # get our list of URLs from a column in the input table
            urlcol = params.get_param_column('urlcol', prev_table)
            if urlcol:
                urls = prev_table[urlcol].tolist()
            else:
                urls = []

        if len(urls) > 0:
            table = pd.DataFrame(
                {'url': urls, 'status': ''},
                columns=['url', 'date', 'status', 'html']
            )

            await scrape_urls(urls, table)

        else:
            table = pd.DataFrame()

        table['date'] = timezone.now().isoformat(timespec='seconds') \
            .replace('+00:00', 'Z')

        result = ProcessResult(dataframe=table)
        # No need to truncate: input is already truncated
        # No need to sanitize: we only added text+date+status

        await ModuleImpl.commit_result(wfm, result)
