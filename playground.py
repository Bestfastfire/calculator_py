import re

exp = "2+[(-2 * -2 + 2 - 3 + 3a) + [2]] + ((!5 /!2) * 3) + (!2)"

verify = [
    {'reg': r'[^\d\{\}\(\)\[\]\+-\/*!\^]+'},
    {'reg': r'\(\)|\[\]|\{\}'},
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


def _calc(symbol, v1, v2=0.0):
    my_log('calculating -> ' + str(v1) + ' ' + symbol + ' ' + str(v2))
    if symbol == '!':
        count = 1
        r = 1

        while count <= v1:
            r *= count
            count += 1

        return r

    elif symbol == '^':
        return v1 ** v2

    elif symbol == '+':
        return v1 + v2

    elif symbol == '-':
        return v1 - v2

    elif symbol == '*':
        return v1 * v2

    elif symbol == '/':
        return v1 / v2

    return v1


def _resolve(expression):
    expression = re.split(out['operations'], expression)
    expression = list(filter(None, expression))
    print('init -> ' + str(expression))

    # resolve all !
    for i in range(len(expression)):
        op = expression[i]

        if '!' in op:
            expression[i] = _calc('!', float(op[1:]))

    # resolve all ^, * and /
    expression = _resolve_last_priority(expression, '^')
    expression = _resolve_last_priority(expression, '*')
    expression = _resolve_last_priority(expression, '/')

    # resolve all + and -
    print('done -> ' + str(expression))
    return ''


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

    # clean empty indexes ['']
    expression = list(filter(None, expression))
    return expression


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
                        match = expression[start:(i+1)]

                        to_add = {
                            'match': match,
                        }

                        sub = match[1:-1]
                        if len(re.findall(out['any_priority'], sub)) > 0:
                            _res = _list_priority(sub)

                            if _res['catch']:
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
        'priority_list': priority_list,
        'catch': catch
    }


for reg in verify:
    exp = re.sub(reg['reg'], reg['rep'] if 'rep' in reg else '', exp)


res = _list_priority(exp)

if res['catch']:
    print('Expressão inválida -> ' + str(res))

else:
    print(str(res))



