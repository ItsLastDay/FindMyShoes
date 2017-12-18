import argparse
from collections import namedtuple, defaultdict
from statistics import mean
from itertools import chain
from math import log2


Result = namedtuple("Result", ['url', 'relevance', 'filters'])
MergedResult = namedtuple("MergedResult", ['url', 'relevances', 'filterss'])


def parse_md(filename: str) -> {str: [Result]}:
    query_prefix = '### '
    relevance_prefix = 'Оценка релевантности:'
    filters_prefix = 'Оценка соответствия фильтрам:'
    current_query = None
    d = defaultdict(lambda : [])
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()

            for i, line in enumerate(lines):
                if line.startswith(query_prefix):
                    current_query = line[len(query_prefix):].strip()
                elif line.startswith('http'):
                    url = line.strip()
                    relevance = int(lines[i + 1][len(relevance_prefix):].strip())
                    filters = int(lines[i + 2][len(filters_prefix):].strip())
                    assert current_query is not None
                    d[current_query].append(Result(url, relevance, filters))
    except Exception as e:
        print("Error while proceeding file \"" + filename + "\": " + str(e))
        return {}
    return d


def merge_assessors(assessors: [{str: [Result]}]) -> {str: [MergedResult]}:
    query_results = defaultdict(lambda: [])
    for ass in assessors:
        for query, results_by_assessor in ass.items():
            query_results[query].append(results_by_assessor)
    d = dict()
    for query, results_by_assessor in query_results.items():
        merged_results = []
        for rs in zip(*results_by_assessor):
            url = rs[0].url
            assert all(map(lambda r: r.url == url, rs))
            relevances = list(map(lambda r: r.relevance, rs))
            filterss = list(map(lambda r: r.filters, rs))
            merged_results.append(MergedResult(url, relevances, filterss))
        assert all(map(lambda rs: len(rs) == len(merged_results), results_by_assessor))
        d[query] = merged_results
    return d


def is_relevant(relevance: float) -> bool:
    RELEVANCE_THRESHOLD = 4
    return relevance >= RELEVANCE_THRESHOLD



def rr(results: [MergedResult]) -> float:
    mean_relevance = map(lambda mr: mean(mr.relevances), results)
    for i, r in enumerate(mean_relevance):
        if is_relevant(r):
            return 1.0 / (i + 1)
    return 0


# https://habrahabr.ru/company/econtenta/blog/303458/
def mAP(results: [MergedResult]) -> float:
    ndocuments = len(results)
    nobjects = len(results[0].relevances)

    def ap(index):
        object_results = map(lambda r: r.relevances[index], results)
        ap_sum = 0
        relevant_count = 0
        for i, r in enumerate(object_results):
            if is_relevant(r):
                relevant_count += 1
            ap_sum += relevant_count / (i + 1)
        return ap_sum / ndocuments

    return mean(ap(i) for i in range(nobjects))


def ndcg(results: [MergedResult]) -> float:
    n = len(results)
    mean_relevance = map(lambda mr: mean(mr.relevances), results)

    def item_income(i_rk):
        # i - 0-based position
        # rk assessor's grade.
        i, rk = i_rk
        return pow(2, rk) - 1 / log2(i + 1 + 1)

    dcg = sum(map(item_income, enumerate(mean_relevance)))
    idcg = sum(map(item_income, zip([1] * n, [5] * n)))

    return dcg / idcg


def err(results: [MergedResult]) -> float:
    return 0


def p10(results: [MergedResult]) -> float:
    n = len(results)
    assert n == 10
    mean_relevance = map(lambda mr: mean(mr.relevances), results)
    return sum(1 for _ in filter(is_relevant, mean_relevance)) / n


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Evaluate metrics for given assessment *.md files.')
    parser.add_argument('files', type=str, nargs='+', help='Files in *.md format.')
    args = parser.parse_args()
    assessors = map(parse_md, args.files)
    merged = merge_assessors(assessors)
    for query, results in merged.items():
        metrics = list(map(lambda f: f(results), (rr, mAP, ndcg, err, p10)))
        print('& {:70s}'.format(query) + ' & '.join(map(lambda metric: "{:5f}".format(metric), metrics)) + " \\\\")


