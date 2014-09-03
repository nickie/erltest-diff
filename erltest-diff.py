#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re, urllib, urlparse
from lxml import etree, html

def usage(prog):
    print """\
Usage: {0} <URL-1> <URL-1>

Examples:
   {0} vanilla/ mine/
   {0} http://erl.ang/tests/vanilla/ http://erl.ang/tests/mine/

The two directory URLs should contain the index.html files produced
when running ts:run().""".format(prog)

def dump(e):
    return html.tostring(e, pretty_print=True, method="html", encoding="utf-8")

def parse_ts_index(url, source):
    L = {}
    root = html.parse(source)
    tbl = root.xpath('//table[@id="SortableTable"]/tbody/tr')
    for row in tbl:
        col = row.xpath('./td')
        etest = col[0].xpath('./a')[0]
        test = etest.text
        logfile = urlparse.urljoin(url, etest.get('href'))
        ok = int(html.tostring(col[3], method="text"))
        failed = int(html.tostring(col[4], method="text"))
        [skipped, user, auto] = map(int,
          re.match('(\d+) \((\d+)/(\d+)\)',
                   html.tostring(col[5], method="text")).groups())
        missing = int(html.tostring(col[6], method="text"))
        L[test] = { 'log': logfile,
                    'tests': { 'ok': ok, 'failed': failed,
                               'skipped': skipped, 'user': user,
                               'auto': auto, 'missing': missing } }
    return L

def parse_ts_suite(source):
    L = {}
    root = html.parse(source)
    tbl = root.xpath('//table[@id="SortableTable"]/tbody/tr')
    for i, row in enumerate(tbl):
        col = row.xpath('./td')
        num = html.tostring(col[0], method="text")
        module = html.tostring(col[1], method="text")
        group = html.tostring(col[2], method="text")
        case = html.tostring(col[3], method="text")
        result = html.tostring(col[6], method="text")
        note = html.tostring(col[7], method="text")
        L[i] = { 'num': num, 'module': module, 'group': group,
                 'case': case, 'result': result, 'note': note }
    return L

if __name__ == '__main__':
    import sys

    if len(sys.argv) < 3:
        usage(sys.argv[0])
        exit(1)

    first = parse_ts_index(sys.argv[1], urllib.urlopen(sys.argv[1]))
    second = parse_ts_index(sys.argv[2], urllib.urlopen(sys.argv[2]))
    interesting = ['ok', 'failed', 'skipped', 'user', 'auto', 'missing']
    suite_interesting = ['num', 'module', 'group', 'case', 'result', 'note']

    for suite in set(first.keys() + second.keys()):
        if first[suite]['tests'] != second[suite]['tests']:
            first_suite = parse_ts_suite(urllib.urlopen(first[suite]['log']))
            second_suite = parse_ts_suite(urllib.urlopen(second[suite]['log']))
            class Mismatch(Exception):
                pass
            def different(i, j):
                if first_suite[i]['module'] != second_suite[j]['module'] \
                or first_suite[i]['group'] != second_suite[j]['group'] \
                or first_suite[i]['case'] != second_suite[j]['case']:
                    raise Mismatch
                return first_suite[i]['result'] != second_suite[j]['result']
            def find_differences():
                i = 0
                j = 0
                L = []
                while True:
                    try:
                        if different(i, j):
                            L.append((i, j))
                        i += 1
                        j += 1
                    except KeyError:
                        L.extend((k, None) for k in first_suite.keys()
                                           if k >= i)
                        L.extend((None, j) for k in second_suite.keys()
                                           if k >= j)
                        return L
                    except Mismatch:
                        d = 0
                        while True:
                            d += 1
                            out_of_bounds = 0
                            try:
                                if different(i+d, j):
                                    L.extend((i+k, None) for k in range(d))
                                    L.append((i+d, j))
                                else:
                                    L.extend((i+k, None) for k in range(d))
                                i += d+1
                                j += 1
                                break
                            except KeyError:
                                out_of_bounds += 1
                            except Mismatch:
                                pass
                            try:
                                if different(i, j+d):
                                    L.extend((None, j+k) for k in range(d))
                                    L.append((i, j+d))
                                else:
                                    L.extend((None, j+k) for k in range(d))
                                i += 1
                                j += d+1
                                break
                            except KeyError:
                                out_of_bounds += 1
                            except Mismatch:
                                pass
                            if out_of_bounds < 2:
                                continue
                            L.extend((k, None) for k in first_suite.keys()
                                               if k >= i)
                            L.extend((None, k) for k in second_suite.keys()
                                               if k >= j)
                            return L
            print suite
            print "<", ", ".join("{}: {}".format(k, first[suite]['tests'][k])
                                 for k in interesting)
            print ">", ", ".join("{}: {}".format(k, second[suite]['tests'][k])
                                 for k in interesting)
            for i, j in find_differences():
                print
                if i is not None:
                    print "<", " ".join(first_suite[i][k]
                                        for k in suite_interesting)
                if j is not None:
                    print ">", " ".join(second_suite[j][k]
                                        for k in suite_interesting)
            print "-"*72
