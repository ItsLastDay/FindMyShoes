#!/usr/bin/env python3
import sys
import time
from queue import PriorityQueue

from queues import DomainQueue, CrawlQueue
from storage import Storage
from page import RobotsProvider, Page


def safe_sleep(duration_secs):
    if duration_secs > 0:
        time.sleep(duration_secs)


def main():
    domains_to_crawl = DomainQueue()
    content_storage = Storage.create_storage()

    # Store pairs <next_possible_fetch_time, CrawlQueue_for_domain>
    time_domains_to_crawl = PriorityQueue()

    robots_info = RobotsProvider()

    while not domains_to_crawl.is_empty():
        # Fetch one more domain from the queue
        new_domain = domains_to_crawl.get_next_domain()

        # Create new CrawlQueue for it
        crawl_queue_for_new_domain = CrawlQueue()
        crawl_queue_for_new_domain.add_pages([new_domain])

        # Put new queue, with next fetch time equal to current time.
        time_domains_to_crawl.put_nowait((time.time(), 
            crawl_queue_for_new_domain))

        while not time_domains_to_crawl.empty():
            fetch_time, page_queue = time_domains_to_crawl.get_nowait()

            if not page_queue.is_empty():
                safe_sleep(fetch_time - time.time())

                cur_page = page_queue.pop()

                if cur_page.can_be_crawled():
                    cur_page.fetch()

                    if cur_page.can_be_stored():
                        content_storage.put_page(cur_page.url, 
                                url.get_cleaned_response())

                    page_queue.add_pages(cur_page.children())

                    # Page is fetched: next access should be delayed.
                    required_delay = \
                            robots_info.get_robots_delay(url.domain)
                    time_domains_to_crawl.put_nowait(
                            (fetch_time + required_delay, 
                                page_queue)
                            )
                else:
                    # Page should not be fetched: we can ignore delay.
                    time_domains_to_crawl.put_nowait((fetch_time, 
                        page_queue)) 

            time_domains_to_crawl.task_done()

    return 0

if __name__ == '__main__':
    sys.exit(main())
