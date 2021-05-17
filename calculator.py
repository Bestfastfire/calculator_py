import re


def _clean_list(m_list):
    return list(filter(None, m_list))


class Calculator:
    _verify = [
        {'reg': r'[^\d\{\}\(\)\[\]\+-\/*!\^]+'},
        {'reg': r'[\s]+'},
        {'reg': r'^\+'},
        #  (+
        {
            'reg': r'([\(\[\{])[\+*\/^]',
            'rep': r'\1'
        },
        # +)
        {
            'reg': r'[\+*\/^]([\)\]\}])',
            'rep': r'\1'
        },
        {
            'reg': r'(([+\-])[+-\/*\^]+)',
            'rep': r'\2'
        },
        {
            'reg': r'(([\/*\^])[\/*\^]+)',
            'rep': r'\2'
        },
        {
            'reg': r'((!)[!]+)',
            'rep': r'\2'
        }
    ]

    _out = {
        'any_priority': r'\(|\[|\{|\)|\}|\]',
        'any_operator': r'![\d.]|.+[+\-*\/^!].+',
        'operations': r'([^\d.!]+)'
    }

    _main_contrary = [')', ']', '}']
    _main = ['(', '[', '{']

    _contrary = {
        '(': ')',
        '[': ']',
        '{': '}'
    }

    def _calc(self, symbol, v1, v2=0.0):
        symbol = re.sub(r'(.).+', r'\1', symbol)
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

        return result

    def verify_all(self, expression):
        for reg in self._verify:
            expression = re.sub(reg['reg'], reg['rep'] if 'rep' in reg else '', expression)

        return expression

    def _resolve(self, expression):
        expression = re.split(self._out['operations'], expression)
        expression = _clean_list(expression)
        # print('init -> ' + str(expression))

        # resolve all !
        for i in range(len(expression)):
            op = expression[i]

            if '!' in op:
                expression[i] = self._calc('!', float(op[1:]))

        # resolve all ^, * and /
        expression = self._resolve_last_priority(expression, '^')
        expression = self._resolve_last_priority(expression, '/')
        expression = self._resolve_last_priority(expression, '*')

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
                        expression[i] = float(expression[i + 1])
                        expression[i + 1] = ''
                        continue

                # [23.0, -3.0, '+']
                # ['23.0', '+', '3.0']
                vx = expression[i + 1]
                is_num = True

                try:
                    float(vx)

                except ValueError:
                    is_num = False

                v2 = vx if is_num else float(expression[i + 2])
                symbol = '+' if is_num else expression[i + 1]
                v1 = float(op)

                expression[i] = self._calc(symbol, v1, v2)
                expression[i + 1] = ''

                if not is_num:
                    expression[i + 2] = ''

                break

            expression = _clean_list(expression)

        v = float(expression[0])
        return '+' + str(v) if v >= 0 else str(v)

    def _resolve_last_priority(self, expression, symbol):
        expression = _clean_list(expression)
        c = True

        while c:
            if symbol + '-' in expression or symbol in expression:
                for i in range(len(expression)):
                    op = str(expression[i])

                    if op == '':
                        continue

                    if symbol in op:
                        # print('ex -' + op + ' | ' + str(i) + ' | ' + str(expression))
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
                        expression[i - 1] = self._calc(symbol, v1, v2)

                        # set next and current with empty to remove it after
                        expression[i + 1] = ''
                        expression[i] = ''

                        # [4, '', '', '*', 4]
                        expression = _clean_list(expression)
                        break

            else:
                c = False

        # clean empties indexes ['']
        return _clean_list(expression)

    def _list_priority(self, expression):
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

                if letter in self._main:
                    in_match = True
                    search = letter

                elif letter in self._main_contrary:
                    catch = True
                    break

            else:
                if letter == search:
                    jump += 1

                else:
                    if letter == self._contrary[search]:
                        if jump == 0:
                            in_match = False
                            match = expression[start:(i + 1)]

                            to_add = {
                                'match': match,
                            }

                            sub = match[1:-1]
                            if len(re.findall(self._out['any_priority'], sub)) > 0:
                                _res = self._list_priority(sub)

                                if _res['catch']:
                                    priority_list.append(to_add)
                                    catch = True
                                    break

                                else:
                                    to_add['inside'] = _res

                            else:
                                to_add['result'] = self._resolve(sub)

                            priority_list.append(to_add)

                        else:
                            jump -= 1

        if in_match:
            catch = True

        return {
            'list': priority_list,
            'catch': catch
        }

    def _expression_replace(self, expression, m_list):
        for i in range(len(m_list)):
            item = m_list[i]
            match = item['match']

            if 'result' in item:
                expression = expression.replace(match, item['result'])
                expression = self.verify_all(expression)

            elif 'inside' in item:
                expression = expression.replace(match, self._expression_replace(match, item['inside']['list']))
                expression = self.verify_all(expression)

        return expression

    def calc(self, expression):
        try:
            exp = self.verify_all(expression)
            res = self._list_priority(exp)

        except ValueError:
            return 'Expressão inválida!'

        if res['catch']:
            return 'Expressão inválida!'

        else:
            need_continue = True

            # 1 + 2 / 4
            # 1 + +0.5
            # +?

            while need_continue:
                exp = self._expression_replace(exp, res['list'])
                exp = self.verify_all(exp)

                if len(re.findall(self._out['any_priority'], exp)) > 0:
                    res = self._list_priority(exp)
                    exp = self._expression_replace(exp, res['list'])
                    continue

                elif len(re.findall(self._out['any_operator'], exp)) > 0:
                    exp = self._resolve(exp)
                    exp = self.verify_all(exp)
                    continue

                need_continue = False

            return 'O resultado é: ' + str(exp)
