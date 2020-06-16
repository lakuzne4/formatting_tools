# main code
import re


def get_brackets_insides(s):
    # брать только верхние подзапросы
    list_of_insides = []
    list_of_coords = []

    list_of_first_level_coords = []
    list_of_first_level_insides = []

    for it, i in enumerate(s):
        if i == '(':
            list_of_coords.append([it, None])
        if i == ')':
            for j_num, j in enumerate(list_of_coords[::-1]):
                if j[1] is None:
                    list_of_coords[-(j_num+1)][1] = it
                    break
            if j_num+1 == len(list_of_coords):
                list_of_first_level_coords.append(list_of_coords[0])
                list_of_coords = []

    for i in list_of_first_level_coords:
        start, finish = i
        list_of_first_level_insides.append(s[start:finish+1])

    return list_of_first_level_insides


def _format_keywords(query_to_process):
    rows = query_to_process.split('\n')
    new_rows = [row.strip() for row in rows if row not in (' ')]
    new_rows2 = []
    for it, row in enumerate(new_rows):
        for word in ['select', 'from', 'order by', 'group by', 'inner', 'left', 'having', 'join', 'where']:
            row = row.replace(
                word, '\n'+word).replace(word.upper(), '\n'+word.upper())
        new_rows2.append(row)
    query_processed = ' '.join(new_rows2)
    return query_processed


def splitby(string: str, list_of_delimeters=None):
    # вернуть список слов вместе с делимитерами в промежутках
    if list_of_delimeters is None:
        list_of_delimeters = [",", " ", "\-", "!", "?", ":"]
    return list(filter(None, re.split(f"([{''.join(list_of_delimeters)}]+)", string)))


def _row_divisor(query):
    S_LIMIT = 80
    rows = query.split('\n')
    new_rows = []
    new_rows_source_nums = []
    for source_row_num, row in enumerate(rows):
        addition = ''
        if len(row) < S_LIMIT:
            new_rows.append(row)
            new_rows_source_nums.append(source_row_num)
        else:
            splitted_row = splitby(row, [' ', ','])

            # найти наибольшее число слов/элементов чтобы помещалось в S_LIMIT
            while len(''.join(splitted_row)) >= S_LIMIT:

                cnt_words = 0
                for i in splitted_row:
                    if len(''.join(splitted_row[:cnt_words]))+len(i) < S_LIMIT:
                        cnt_words += 1
                    else:
                        break

                new_rows.append(addition+''.join(splitted_row[:cnt_words]))

                added_row = ''.join(splitted_row[:cnt_words]).lower()
                if ' on ' in added_row or 'select ' in added_row or 'group by ' in added_row:
                    addition = '->'*5

                new_rows_source_nums.append(source_row_num)
                splitted_row = splitted_row[cnt_words:]

            new_rows.append(addition+''.join(splitted_row))
            new_rows_source_nums.append(source_row_num)

    return '\n'.join([i for i in new_rows if i not in ['', '  ', '\n'] and not i.isspace()]),\
        [j for i, j in zip(new_rows, new_rows_source_nums) if i not in [
            '', '  ', '\n'] and not i.isspace()]


def _detach_indentations(s: str, indent):
    row_idxs = []
    for row in s.split('\n'):
        row_idxs.append([(m.start(), m.end())
                         for m in re.finditer(f'^({indent})+', row)])
    limit_of_indentation = [i[0][1] if i else 0 for i in row_idxs]

    new_s = []
    indents = []
    for row_num, row in enumerate(s.split('\n')):
        new_s.append(row[limit_of_indentation[row_num]:])
        indents.append(row[:limit_of_indentation[row_num]])
    new_s = '\n'.join(new_s)
    return new_s, indents


def _attach_indentations(s: str, indents, numbers):
    new_s = []
    for row, source_idx in zip(s.split('\n'), numbers):
        new_s.append(indents[source_idx]+row)
    return '\n'.join(new_s)


def row_divisor_indent(query, indentation='\t'):
    query_to_process, indents = _detach_indentations(query, indent='->')
    query_processed, numbers = _row_divisor(query_to_process)
    query_processed = _attach_indentations(
        query_processed, indents=indents, numbers=numbers)
    return query_processed


def format_query_indentation(data, depth=None):
    if depth is None:
        depth = 0

    MAX_DEPTH = 10
    INDENT = ('->'*5)
    if '(' not in data:
        query_to_process = data
        query_processed = _format_keywords(query_to_process)
        query_processed = row_divisor_indent(query_processed)

    else:
        all_subqueries = get_brackets_insides(data)
        all_subqueries = [i for i in all_subqueries if 'select' in i.lower()]

        if len(all_subqueries) == 0:
            query_to_process = data
            query_processed = _format_keywords(query_to_process)
            query_processed = row_divisor_indent(query_processed)

        else:

            query_to_process = data
            for num, subquery in enumerate(all_subqueries):
                query_to_process = query_to_process.replace(
                    subquery, f'пыщпыщ{num}', 1)

            query_processed = _format_keywords(query_to_process)
            query_processed = row_divisor_indent(query_processed)

            new_all_subqueries = []
            for num, subquery in enumerate(all_subqueries):
                if depth < MAX_DEPTH:
                    subquery = '(\n'+format_query_indentation(
                        subquery[1:-1], depth=depth+1)+'\n)'
                    subquery = row_divisor_indent(subquery)
                    new_all_subqueries.append(subquery)

            for num, new_subquery in enumerate(new_all_subqueries):
                query_processed = query_processed.replace(f'пыщпыщ{num}', f'\nпыщпыщ{num}').replace(f'пыщпыщ{num}',
                                                                                                    new_subquery)

    return "\n".join([str(INDENT)+i for i in query_processed.split('\n')])
