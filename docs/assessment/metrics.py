import argparse
from collections import namedtuple, defaultdict
from statistics import mean
from math import log2

from operator import mul, add
from functools import reduce, partial


Result = namedtuple('Result', ['url', 'relevance', 'filters'])
MergedResult = namedtuple('MergedResult', ['url', 'relevances', 'filterss'])


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
        print('Error while proceeding file \'' + filename + '\': ' + str(e))
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


MIN_RELEVANCE = 1
MAX_RELEVANCE = 5
def is_relevant(relevance: float) -> bool:
    RELEVANCE_THRESHOLD = 3
    return relevance >= RELEVANCE_THRESHOLD


def get_relevances(r: MergedResult):
    return r.relevances


def get_filterss(r: MergedResult):
    return r.filterss


def rr(results: [MergedResult], get_grades=get_relevances, is_relevant_func=is_relevant) -> float:
    mean_grades = map(lambda mr: mean(get_grades(mr)), results)
    for i, r in enumerate(mean_grades):
        if is_relevant_func(r):
            return 1.0 / (i + 1)
    return 0


# https://habrahabr.ru/company/econtenta/blog/303458/
def mAP(results: [MergedResult], get_grades=get_relevances, is_relevant_func=is_relevant) -> float:
    ndocuments = len(results)
    nobjects = len(get_grades(results[0]))

    def ap(index):
        object_results = map(lambda r: get_grades(r)[index], results)
        ap_sum = 0
        relevant_count = 0
        for i, r in enumerate(object_results):
            if is_relevant_func(r):
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
        return (pow(2, rk) - 1) / log2(i + 1 + 1)

    dcg = sum(map(item_income, enumerate(mean_relevance)))
    idcg = sum(map(item_income, zip([1] * n, [MAX_RELEVANCE ] * n)))

    return dcg / idcg


def err_relevance(results: [MergedResult], theta: float=0.9) -> float:
    n = len(results)
    mean_relevance = list(map(lambda mr: mean(mr.relevances), results))

    def rel_prob(relevance):
        # relevance probability.
        return pow(2, relevance - MIN_RELEVANCE) / pow(2, MAX_RELEVANCE - 1)

    err_sum = 0
    for k in range(n):
        err_sum += 1 / (k + 1) * pow(theta, k) * rel_prob(mean_relevance[k]) * \
            reduce(mul, map(lambda r: 1 - rel_prob(r), mean_relevance[:k]), 1)
    return err_sum


def p10(results: [MergedResult], get_grades=get_relevances, is_relevant_func=is_relevant) -> float:
    n = len(results)
    assert n == 10
    mean_grades = map(lambda mr: mean(get_grades(mr)), results)
    return sum(1 for _ in filter(is_relevant_func, mean_grades)) / n


def print_metrics(metrics, query_string):
    print(query_string + ' & ' + ' & '.join(map(lambda metric: '{:.4g}'.format(metric), metrics)) + ' \\\\')


def do_metrics(merged, functions: list, functions_names=None):
    full_metrics = []
    if functions_names is not None:
        print('query & ' + ' & '.join(functions_names) + ' \\\\')
        print('\\hline')
    for iquery, results in enumerate(sorted(merged.values())):
        metrics = list(map(lambda f: f(results), functions))
        full_metrics.append(metrics)
        print_metrics(metrics, str(1 + iquery))

    nmetrics = len(full_metrics[0])
    assert all(map(lambda metrics: len(metrics) == nmetrics, full_metrics))

    nqueries = len(full_metrics)
    sum_metrics = reduce(lambda m1, m2: map(lambda r1r2: sum(r1r2), zip(m1, m2)), full_metrics, [0] * nmetrics)
    avg_metrics = map(lambda metric: metric / nqueries, sum_metrics)
    print_metrics(avg_metrics, 'avg.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Evaluate metrics for given assessment *.md files.')
    parser.add_argument('files', type=str, nargs='+', help='Files in *.md format.')
    args = parser.parse_args()
    assessors = map(parse_md, args.files)
    merged = merge_assessors(assessors)

    print('### relevance ###')
    do_metrics(merged, [rr, mAP, ndcg, err_relevance, p10], ['RR', 'MAP', 'NDCG', 'ERR', 'P@10'])


    print('\n### filters ###')
    is_relevant_filter = lambda x: x > 0.5
    filters_metrics = list(map(lambda foo: partial(foo, get_grades=get_filterss, is_relevant_func=is_relevant_filter), [mAP, p10]))
    do_metrics(merged, filters_metrics, ['MAP', 'P@10'])

    # print()
    # for query in sorted(merged.keys()):
    #     print('\\item \\texttt{{{}}}'.format(query))
