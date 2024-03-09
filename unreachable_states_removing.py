# Недетерминированный конечный автомат задан в виде таблицы переходов.
# Напишите программу, которая считает эту таблицу из файла
# и удалит из него недостижимые состояния

# Для чтения таблицы переходов из файла
import csv

# Название файла с описанием функции переходов
input_filename = 'input.csv'
# Название файла для записи новой функции переходов
output_filename = 'output.csv'

# Класс недетерминированного конечного автомата
class NondeterministicFiniteAutomaton:
    def __init__(self):
        # Множество состояний
        self.Q = set()
        # Множество входных символов
        self.Sigma = set()
        # Функция переходов
        self.delta = dict()
        # Начальное состояние
        self.q0 = 'q0'
        # Множество финальных состояний
        self.F = set()

    def load_transition_function(self, filename):
        # Функция будет представлять собой словарь в формате
        # функция[(состояние, символ)] = {множество состояний}
        transition_function = dict()
        with open(filename) as f:
            reader_obj = csv.reader(f, delimiter=';')
            symbols = []
            # Смотрим все строки файла
            for row_count, row in enumerate(reader_obj):
                # Получаем список символов
                if row_count == 0:
                    symbols = row[2:]
                    self.Sigma = set(symbols)
                # Получаем список переходов
                else:
                    is_final = False
                    state = ''
                    for i in range(len(row)):
                        # Является ли состояние финальным
                        if i == 0:
                            if row[i] == '+':
                                is_final = True
                        # Состояние, из которого переходим
                        elif i == 1:
                            state = row[i]
                            if is_final:
                                self.F.add(state)
                            self.Q.add(state)
                            if row_count == 1:
                                self.q0 = state
                        # Состояния, в которые переходим по символу
                        else:
                            transition_function[(state, symbols[i - 2])] = set(row[i][1:-1].split(','))
        self.delta = transition_function

    # Удалить недостижимые состояния
    def remove_unreachable_states(self):
        new_Q = set()
        new_reachable_states = {self.q0}
        # Продолжаем, пока множество достижимых состояний не перестанет изменяться
        while new_reachable_states != set():
            new_Q.update(new_reachable_states)
            added_states = new_reachable_states
            new_reachable_states = set()
            # Рассматриваем все состояния, которых достигли на предыдущем шаге
            for state in added_states:
                # Для всех символов
                for c in self.Sigma:
                    # Добавляем новые достигнутые состояния
                    for q in self.delta[(state, c)]:
                        if q not in new_Q:
                            new_reachable_states.add(q)

        # Обновление состояний
        self.Q = new_Q

        # Обновление финальных состояний
        new_F = set()
        for q in self.F:
            if q in self.Q:
                new_F.add(q)
        self.F = new_F

        # Обновление функции переходов
        new_transition_function = dict()
        for k in self.delta.keys():
            if k[0] in self.Q:
                new_transition_function[k] = self.delta[k]
        self.delta = new_transition_function

    # Запись таблицы переходов в файл
    def write_into_file(self, filename):
        # Символы входного алфавита
        symbols = [c for c in self.Sigma]
        symbols.sort()
        # Таблица переходов для записи
        table = [['is_final', 'state'] + symbols]
        # Все состояния
        states = list(self.Q)
        states.sort()
        for i in range(len(states)):
            line = ['' for _ in range(len(table[0]))]
            # Проверяем, является ли состояние финальным
            if states[i] in self.F:
                line[0] = '+'
            else:
                line[0] = '-'
            line[1] = states[i]
            # Записываем все переходы
            for j in range(len(symbols)):
                line[j + 2] = '{' + ','.join(sorted(self.delta[(states[i], symbols[j])])) + '}'
            # Добавляем в итоговую таблицу
            table.append(line)

        # Запись результатов в файл
        with open(filename, 'w', newline='\n') as f:
            writer_obj = csv.writer(f, delimiter=';')
            writer_obj.writerows(table)


if __name__ == '__main__':
    finite_automaton = NondeterministicFiniteAutomaton()
    finite_automaton.load_transition_function(input_filename)
    finite_automaton.remove_unreachable_states()
    finite_automaton.write_into_file(output_filename)