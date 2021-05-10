import re

exp = "2+[]((2 * 2) + 2) + ((2 /2) * 3) + (2)"

verify = [
    {'reg': r'\(\)|\[\]|\{\}'},
    {'reg': r'[\s]'}
]

out = {
    'any_priority': r'\(|\[|\{|\)|\}|\]',
}

main_contrary = [')', ']', '}']
main = ['(', '[', '{']

contrary = {
    '(': ')',
    '[': ']',
    '{': '}'
}


def _calc(v1, v2=0.0, symbol='+'):
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

    return ''


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



