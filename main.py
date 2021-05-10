import re

log_on = False

priorityLevel = [
    r'![\d.]+',
    r'[-]?[\d.]+\^[-]?[\d.]+',
    r'\((?:[^()]|(?R))+\)'
    r'\[.+?\]',
    r'\{.+?\}',
    r'[-]?[\d.]+\*[-]?[\d.]+',
    r'[-]?[\d.]+\/[-]?[\d.]+',
    r'[-]?[\d.]+\+[\d.]+',
    r'[-]?[\d.]+-[\d.]+'
]

verifyReg = [
    {'reg': r'[^\d\{\}\(\)\[\]\+-\/*!\^]+'},
    {
        'reg': r'(([+\-])[+-\/*\^]+)',
        'rep': r'\2'
    },
    {
        'reg': r'((!)[!]+)',
        'rep': r'\2'
    }
]


def my_log(self, *args):
    if log_on:
        print(self, args)


def _check_high_priority(express):
    priorities = [['(', ')'], ['{', '}'], ['[', ']']]
    count = 0

    for _p in priorities:
        bef = _p[0]
        aft = _p[1]
        local = 0

        for letter in express:
            if letter == bef:
                local = count + 1

            elif letter == aft:
                local = count - 1

        count = count + (1 if local > 0 else 0)

    return True if count == 0 else False


def _calc(e, v1, v2=0.0, symbol='+'):
    if '!' in e:
        count = 1
        r = 1

        while count <= v1:
            r *= count
            count += 1

        return r

    elif len(e) == 1:
        return v1

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

    return 0


def _calculator(express):
    #  ['2', '*', '', '(', '36.0', ')', '']
    express = re.sub(r'([\[\{\(])([+\-!]?[\d.]+)([\]\}\)])', r'\2', express)

    # ['2', '*', '', '+', '6.0']
    express = re.sub(r'([*\-\/+])\+', r'\1', express)

    complement = ''

    if '*-' in express or '/-' in express or '^-' in express or express[0] == '-':
        complement = '\-'

    if '!' in express:
        complement += '!'

    e = re.split(r'([^\w.' + complement + '])', express)
    my_log('calculator -> ' + express + ' | ' + str(e))

    for i in range(len(e)):
        item = e[i]

        if '!' in item:
            e[i] = _calc('!', float(item[1]))

    if len(e) == 1:
        return e[0]

    v1 = float(e[0])
    v2 = float(e[2])

    v3 = float(e[4]) if len(e) > 3 else 0
    op2 = e[3] if len(e) > 3 else '+'

    result = _calc(e, v1, v2, e[1])
    result = _calc(e, result, v3, op2)

    my_log('result -> ' + str(result))

    if result == 0:
        return 0

    return result


def _has_more(express, p_list, small=1):
    count = 0

    for pl in p_list:
        my_log('has_more -> ', express, ' | ', pl, ' | ', len(re.findall(pl, express)))
        count = count + len(re.findall(pl, express))

    return count > small


def _remove_special(old, new):
    contrary = {
        '{': '}',
        '}': '{',
        '[': ']',
        ']': '[',
        '(': ')',
        ')': '('}

    if _check_high_priority(new):
        return new

    else:
        # ['[{4*2}*2', '+', '{3+2}*3]']
        ex = re.split(r'[)}\]]([+-\/*]+)[({\[]', old)
        my_log('ex -> ' + str(ex))

        s = 0
        for i in range(len(ex)):
            item = ex[i]

            if len(item) > 1:
                if s % 2 == 0:
                    ex[i] = item + contrary[item[0]]

                else:
                    ex[i] = contrary[item[-1]] + item

                s = s + 1
                my_log('try with -> ' + ex[i])
                while _has_more(ex[i], priorityLevel, 0):
                    for _p in priorityLevel:
                        ex[i] = _broke(ex[i], _p, priorityLevel)

        return ''.join(ex)


def _broke(express, priority, p_list):
    cut = re.findall(priority, express)
    my_log('receiver -> ' + str(cut) + ' | ' + priority)

    # case found this express
    if len(cut) > 0:
        for c in cut:
            new = c

            # case is special, remove the characters
            if c[0] in ['(', '{', '[']:
                new = _remove_special(new, new[1:-1])
                # ('[{4*2}*2]+[{3+2}*3]', ' to ', '[{4*2}*2]+[{3+2}*3]')
                my_log('removing start and end -> ', c, ' to ', new)

            if _has_more(new, p_list):
                for pr in p_list:
                    express = express.replace(new, _broke(new, pr, p_list))

            else:
                my_log('calling calculator -> ' + new)
                test = express.split(c)
                rpl = str(_calculator(new))
                rg = r'[+\-*\/]'

                # last 3 -3/3
                if len(re.findall(rg, test[-1])) == 0 and len(re.findall(rg, rpl[0])) == 0:
                    express = express.replace(c, '+' + str(_calculator(new)))

                else:
                    express = express.replace(c, str(_calculator(new)))

                my_log('ex -> ' + express)

    # Fix error when (x) / [x] / {x}
    else:
        regx = r'(\(|\[\{)[\d.](\)\}\])'
        f = re.findall(regx, express)

        if len(f) > 0 and f[0] == express:
            return re.sub(r'[^\d.]', '', express)

    my_log('returning -> ' + express)
    return express


somethingWrong = True
while somethingWrong:
    expression = input('Digite uma expressão matemática:\n')
    somethingWrong = False

    # remove any out characters
    for reg in verifyReg:
        expression = re.sub(reg['reg'], reg['rep'] if 'rep' in reg else '', expression)

    # checks if expressions has high priority args
    highPriority = re.findall(r'\(|\)|\[|]|\{|}', expression)

    if len(highPriority) > 0:
        res = _check_high_priority(expression)

        if not res:
            print('Expressão matemática inválida, tente novamente!')
            somethingWrong = True
            continue

    resolution = [str(expression)]

    while _has_more(expression, priorityLevel, 0):
        for p in priorityLevel:
            expression = _broke(expression, p, priorityLevel)
            expression = _broke(expression, p, priorityLevel)

            if expression not in resolution:
                resolution.append(str(expression))

    print('Fazendo operações:\n' + '\n'.join(resolution) + '\nO resultado é: ' + expression)
