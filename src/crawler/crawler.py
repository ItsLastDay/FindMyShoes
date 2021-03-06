#!/usr/bin/env python3
import sys
import time
from logging import getLogger
import logging.config
from queue import PriorityQueue
from collections import defaultdict

from page import Page
from queues import DomainQueue, CrawlQueue
from storage import LocalStorage, GDriveStorage
from robots import RobotsProvider

from url_getter import URLGetter


main_crawler_logger = getLogger("main_crawler")


def safe_sleep(duration_secs):
    if duration_secs > 0:
        time.sleep(duration_secs)


def main():
    domains_to_crawl = DomainQueue()
    # content_storage = GDriveStorage.create_storage()
    content_storage = LocalStorage.create_storage()

    # Store pairs <next_possible_fetch_time, CrawlQueue_for_domain>
    time_domains_to_crawl = PriorityQueue()

    robots_info = RobotsProvider()

    url_fails = defaultdict(lambda: 0)

    while domains_to_crawl.has_next():
        # Fetch one more domain from the queue
        new_domain = domains_to_crawl.get_next_domain()
        main_crawler_logger.info("Received new domain to crawl: {}".format(new_domain))

        # Create new CrawlQueue for it
        crawl_queue_for_new_domain = CrawlQueue()
        crawl_queue_for_new_domain.add_pages([Page(new_domain)])

        # Put new queue, with next fetch time equal to current time.
        time_domains_to_crawl.put_nowait((time.time(),
                                          crawl_queue_for_new_domain))

        while not time_domains_to_crawl.empty():
            fetch_time, page_queue = time_domains_to_crawl.get_nowait()
            main_crawler_logger.debug('Fetched {}, {} from priority queue'.format(fetch_time, page_queue))

            if not page_queue.is_empty():
                safe_sleep(fetch_time - time.time())

                cur_page = page_queue.pop()

                if robots_info.can_be_crawled(cur_page):
                    try:
                        cur_page.fetch()

                        if cur_page.can_be_stored():
                            content_storage.put_page(cur_page.url(),
                                                     cur_page.get_cleaned_response())

                        page_queue.add_pages(cur_page.children())

                        # Page is fetched: next access should be delayed.
                        required_delay = robots_info.get_robots_delay(new_domain)
                        time_domains_to_crawl.put_nowait((fetch_time + required_delay, page_queue))
                    except Exception as e:
                        main_crawler_logger.error(e)
                        # Seen errors: 
                        # apiclient.errors.HttpError: <HttpError 403 when requesting https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&alt=json returned "User rate limit exceeded.">
                        # requests.exceptions.ConnectionError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response',))
                        URLGetter.restart_sesison()
                        print('sleeping')
                        time.sleep(10)
                        url_fails[cur_page.url()] += 1
                        if url_fails[cur_page.url()] < 3:
                            page_queue.add_page(cur_page)

                        time_domains_to_crawl.put_nowait((fetch_time, page_queue))
                else:
                    # Page should not be fetched: we can ignore delay.
                    time_domains_to_crawl.put_nowait((fetch_time, page_queue))

            time_domains_to_crawl.task_done()

    return 0


if __name__ == '__main__':
    # from threading import current_thread
    # logging.basicConfig(filename='./logs/crawler_debug_{}.log'.format(current_thread().ident), level=logging.DEBUG)
    import sys

    if len(sys.argv) > 1:
        log_filename = './logs/crawler_debug_{}.log'.format(sys.argv[1])
    else:
        log_filename = './logs/crawler_debug.log'
    logging.basicConfig(filename=log_filename, level=logging.DEBUG, filemode='w',
                        format='%(asctime)s %(levelname)s:%(name)s:%(message)s')
    sys.exit(main())
