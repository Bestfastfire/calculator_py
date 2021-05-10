import re

log_on = False

out = {
    'wh_priority': r'\(|\)|\[|]|\{|}',
    'high_priority': [['(', ')'], ['{', '}'], ['[', ']']]
}

priorityLevel = [
    r'\(.+?\)',
    r'\[.+?\]',
    r'\{.+\}',
    r'![\d.]+',
    r'[-]?[\d.]+\^[-]?[\d.]+',
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


def _verify_priority(express):
    count = 0

    for p in out['high_priority']:
        bef = p[0]
        aft = p[1]
        local = 0

        for letter in express:
            if letter == bef:
                local = count + 1

            elif letter == aft:
                local = count - 1

        count = count + (1 if local > 0 else 0)

    return True if count == 0 else False


needContinue = True
while needContinue:
    expression = input('Digite uma expressão matemática:\n')
    needContinue = False

    # remove any out characters
    for reg in verifyReg:
        expression = re.sub(reg['reg'], reg['rep'] if 'rep' in reg else '', expression)

    # checks if expressions has high priority args
    if len(re.findall(out['wh_priority'], expression)) > 0 and True:
        print('')