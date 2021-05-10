import re

verify = [
    {'reg': r'[^\d\{\}\(\)\[\]\+-\/*!\^]+'},
    {'reg': r'[\s]+'},
    {'reg': r'^\+'},
    {
        'reg': r'([\(\[\{])[\+*\/^]',
        'rep': r'\1'
    },
    {
        'reg': r'[\+*\/^]([\)\]\}])',
        'rep': r'\1'
    },
    {
        'reg': r'(([+\-])[+-\/*\^]+)',
        'rep': r'\2'
    },
    {
        'reg': r'((!)[!]+)',
        'rep': r'\2'
    }
]

out = {
    'any_priority': r'\(|\[|\{|\)|\}|\]',
    'any_operator': r'.+[+\-*/].+',
    'operations': r'([^\d.!]+)'
}

main_contrary = [')', ']', '}']
main = ['(', '[', '{']

contrary = {
    '(': ')',
    '[': ']',
    '{': '}'
}

log_on = False


def my_log(self, *args):
    if log_on:
        print(self, args)


def _verify_all(expression):
    for reg in verify:
        expression = re.sub(reg['reg'], reg['rep'] if 'rep' in reg else '', expression)

    return expression


def _calc(symbol, v1, v2=0.0):
    symbol = re.sub(r'(.).+', r'\1', symbol)
    my_log('calculating -> ' + str(v1) + ' ' + symbol + ' ' + str(v2))
    result = v1

    v1 = float(v1)
    v2 = float(v2)

    if symbol == '!':
        count = 1
        _r = 1

        while count <= v1:
            _r *= count
            count += 1

        result = _r

    elif symbol == '^':
        result = v1 ** v2

    elif symbol == '+':
        result = v1 + v2

    elif symbol == '-':
        result = v1 - v2

    elif symbol == '*':
        result = v1 * v2

    elif symbol == '/':
        result = v1 / v2

    my_log('result -> ' + str(result))
    return result


def clean_list(m_list):
    return list(filter(None, m_list))


def _resolve(expression):
    expression = re.split(out['operations'], expression)
    expression = clean_list(expression)
    # print('init -> ' + str(expression))

    # resolve all !
    for i in range(len(expression)):
        op = expression[i]

        if '!' in op:
            expression[i] = _calc('!', float(op[1:]))

    # resolve all ^, * and /
    expression = _resolve_last_priority(expression, '^')
    expression = _resolve_last_priority(expression, '/')
    expression = _resolve_last_priority(expression, '*')

    # resolve all + and -

    # ['-', '2', '?', '2']
    if expression[0] == '-':
        expression[1] = str(-float(expression[1]))
        expression[0] = ''

    while len(expression) > 1:
        size = len(expression)

        for i in range(size):
            op = expression[i]

            if op == '' or i == size - 1:
                continue

            # ['+', '9']
            if size == 2:
                try:
                    float(expression[i])

                except ValueError:
                    expression[i] = float(expression[i+1])
                    expression[i+1] = ''
                    continue

            # [23.0, -3.0, '+']
            # ['23.0', '+', '3.0']
            my_log('ex -> ' + str(expression))
            vx = expression[i + 1]
            is_num = True

            try:
                float(vx)

            except ValueError:
                is_num = False

            v2 = vx if is_num else float(expression[i + 2])
            symbol = '+' if is_num else expression[i + 1]
            v1 = float(op)

            expression[i] = _calc(symbol, v1, v2)
            expression[i + 1] = ''

            if not is_num:
                expression[i + 2] = ''

            break

        expression = clean_list(expression)

    v = float(expression[0])
    return '+' + str(v) if v >= 0 else str(v)


def _resolve_last_priority(expression, symbol):
    if symbol + '-' in expression or symbol in expression:
        for i in range(len(expression)):
            op = str(expression[i])

            if op == '':
                continue

            if symbol in op:
                # ex: ['-', '2', 'symbol-', '2']
                v1 = float(expression[i - 1])
                v2 = float(expression[i + 1])

                # if index before contain -
                if i > 1 and '-' in expression[i - 2]:
                    # remove - of last
                    expression[i - 2] = expression[i - 2][0:-1]
                    v1 = v1 * -1

                if '-' in op:
                    v2 = v2 * -1

                # set last index with result
                expression[i - 1] = _calc(symbol, v1, v2)

                # set next and actual with empty to remove after
                expression[i + 1] = ''
                expression[i] = ''

    # clean empties indexes ['']
    return clean_list(expression)


def _list_priority(expression):
    priority_list = []
    in_match = False
    catch = False
    search = ''
    start = 0
    jump = 0

    for i in range(len(expression)):
        letter = expression[i]

        if not in_match:
            start = i

            if letter in main:
                in_match = True
                search = letter

            elif letter in main_contrary:
                catch = True
                break

        else:
            if letter == search:
                jump += 1

            else:
                if letter == contrary[search]:
                    if jump == 0:
                        in_match = False
                        match = expression[start:(i + 1)]

                        to_add = {
                            'match': match,
                        }

                        sub = match[1:-1]
                        if len(re.findall(out['any_priority'], sub)) > 0:
                            _res = _list_priority(sub)

                            if _res['catch']:
                                priority_list.append(to_add)
                                catch = True
                                break

                            else:
                                to_add['inside'] = _res

                        else:
                            to_add['result'] = _resolve(sub)

                        priority_list.append(to_add)

                    else:
                        jump -= 1

    if in_match:
        catch = True

    return {
        'list': priority_list,
        'catch': catch
    }


def _expression_replace(expression, m_list):
    for i in range(len(m_list)):
        item = m_list[i]
        match = item['match']

        if 'result' in item:
            my_log('match -> ' + match + ' replace -> ' + item['result'])
            expression = expression.replace(match, item['result'])
            expression = _verify_all(expression)

        elif 'inside' in item:
            expression = expression.replace(match, _expression_replace(match, item['inside']['list']))
            expression = _verify_all(expression)

    return expression


want_continue = True
while want_continue:
    # exp = "2+(-2 * -2 + 2 - 3 + 3) + (2) + ((120 /2) * 3) + (2)"
    try:
        exp = input("Digite uma expressão matemática:\n")

    except ValueError:
        print('Expressão inválida!')
        continue

    exp = _verify_all(exp)
    res = _list_priority(exp)

    if res['catch']:
        print('Expressão inválida! -> ' + str(res))
        continue

    else:
        print('Iniciando cálculos:\n' + exp)
        need_continue = True

        # 1 + 2 / 4
        # 1 + +0.5
        # +?

        while need_continue:
            exp = _expression_replace(exp, res['list'])
            exp = _verify_all(exp)

            if len(re.findall(out['any_priority'], exp)) > 0:
                res = _list_priority(exp)
                exp = _expression_replace(exp, res['list'])
                print(exp)

                continue

            elif len(re.findall(out['any_operator'], exp)) > 0:
                exp = _resolve(exp)
                exp = _verify_all(exp)
                print(exp)
                continue

            need_continue = False

        print('O resultado é: ' + str(exp))
        r = input('Digite "c" para uma nova expressão ou qualquer outro caractere para finalizar:\n')

        if r != 'c':
            want_continue = False
