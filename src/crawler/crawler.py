#!/usr/bin/env python3
import sys
import time
from queue import PriorityQueue

from queues import DomainQueue, CrawlQueue
from storage import Storage

def main():
    domains_to_crawl = DomainQueue()
    storage = Storage.create_storage()

    # Store pairs <next_possible_fetch_time, CrawlQueue_for_domain>
    time_domains_to_crawl = PriorityQueue()

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
            fetch_time, url_queue = time_domains_to_crawl.get_nowait()

            

            time_domains_to_crawl.task_done()




    return 0

if __name__ == '__main__':
    sys.exit(main())
