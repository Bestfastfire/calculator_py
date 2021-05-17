# pip install pysimplegui

import PySimpleGUI as sg
import calculator as cl


def btn(txt=''):
    btn = sg.Button(size=(6, 3), button_text=txt)
    return btn


class LayoutCalculator:
    def __init__(self):
        self.calc = cl.Calculator()
        self.layout = [
            [sg.InputText(size=(36, 5), key='txt')],
            [sg.Text(key='alert', text='Digite uma equação acima')],
            [btn(txt='('), btn(txt=')'), btn(txt='C'), btn(txt='⌫')],
            [btn(txt='x^y'), btn(txt='x^2'), btn(txt='n!'), btn(txt='/')],
            [btn(txt='7'), btn(txt='8'), btn(txt='9'), btn(txt='*')],
            [btn(txt='4'), btn(txt='5'), btn(txt='6'), btn(txt='-')],
            [btn(txt='1'), btn(txt='2'), btn(txt='3'), btn(txt='+')],
            [btn(txt='+/-'), btn(txt='0'), btn(txt='.'), btn(txt='=')]
        ]

        self.window = sg.Window("Calculadora").layout(self.layout)
        # self.button, self.values = self.window.read()

    def show(self):
        out = {
            'x^y': '^',
            'x^2': '^2',
            'n!': '!'
        }

        while True:
            self.event, self.values = self.window.read()
            if self.event == sg.WIN_CLOSED:
                break

            else:
                txt = self.layout[0][0]
                alert = self.layout[1][0]
                exp = self.values['txt']

                if self.event in out:
                    exp += out[self.event]

                else:
                    if self.event == 'C':
                        exp = ''

                    elif self.event == '⌫':
                        exp = exp[0:-1]

                    elif self.event != '=':
                        exp += self.event

                try:
                    calc = self.calc.calc(exp)

                except:
                    calc = 'Expressão inválida!'

                alert.update(calc)
                txt.update(exp)


screen = LayoutCalculator()
screen.show()
