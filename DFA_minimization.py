# Детерминированный конечный автомат задан в виде таблицы переходов.
# Напишите программу, которая считает эту таблицу из файла
# и с помощью алгоритма минимизации удаляет все неразличимые состояния

# Для чтения таблицы переходов из файла
import csv
# Для получения всех цепочек символов заданной длины
import itertools

# Название файла с описанием функции переходов
input_filename = 'input.csv'
# Название файла для записи новой функции переходов
output_filename = 'output.csv'


# Класс детерминированного конечного автомата
class FiniteAutomaton:
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

    # Загрузить данные о функции переходов
    def load_transition_function(self, filename):
        # Функция будет представлять собой словарь в формате
        # функция[(текущее состояние, символ)] = новое состояние
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
                        # Состояние, в которое переходим по символу
                        else:
                            transition_function[(state, symbols[i-2])] = row[i]
        self.delta = transition_function

    # Разбиение на классы эквивалентности
    def __find_equivalence_classes(self):
        # Начальное разбиение
        equivalence_classes = [self.F, self.Q.difference(self.F)]
        # Начальная длина цепочки символов
        current_chain_length = 1

        # Повторяем алгоритм, пока новое разбиение не будет таким же, как старое
        while True:
            # Новое разбиение
            new_equivalence_classes = []
            # Все возможные цепочки символов текущей длины
            chains = [p for p in itertools.product(self.Sigma, repeat=current_chain_length)]
            # Каждый класс будем пытаться разбить
            for eq_cl in equivalence_classes:
                # Ключ: строка из классов, в которые попадаем из какого-то состояния по всем цепочкам
                # Значение: множество всех таких состояний
                clases_table = dict()
                # Для каждого состояния в текущем классе эквивалентности
                for state in eq_cl:
                    # Cтрока из классов, в которые попадаем из текущего состояния по всем цепочкам
                    classes = ''
                    # Последовательно перебираем все цепочки
                    for chain in chains:
                        current_state = state
                        # Переходим в следующее состояние по символу
                        for c in chain:
                            current_state = self.delta[(current_state, c)]
                        # Ищем класс эквивалентности, в котором содержится последнее полученное состояние
                        for i in range(len(equivalence_classes)):
                            if current_state in equivalence_classes[i]:
                                # Добавляем этот класс к строке
                                classes += str(i)
                                break
                    # Добавляем в словарь состояние, которое можно получить по текущей строке классов
                    if classes in clases_table:
                        clases_table[classes].add(state)
                    else:
                        clases_table[classes] = {state}
                # Добавляем классы из новых разбиений
                for k in clases_table.keys():
                    new_equivalence_classes.append(clases_table[k])
            if new_equivalence_classes == equivalence_classes:
                break
            # Обновляем текущее разбиение
            equivalence_classes = new_equivalence_classes
            # Увеличиваем длину цепочки символов
            current_chain_length += 1

        return equivalence_classes

    # Алгоритм минимизации
    def minimize(self):
        # Находим классы эквивалентности
        equivalence_classes = self.__find_equivalence_classes()
        # Ищем, в каком классе находится начальное состояние
        initial_state_class = 0
        for i in range(len(equivalence_classes)):
            if self.q0 in equivalence_classes[i]:
                initial_state_class = i
                break
        # Класс с начальным состоянием ставим в начало
        if initial_state_class != 0:
            equivalence_classes[0], equivalence_classes[initial_state_class] = equivalence_classes[initial_state_class], equivalence_classes[0]

        # Обновление функции переходов
        new_transition_function = dict()
        # Для каждого класса эквивалентности определим новый переход
        for i in range(len(equivalence_classes)):
            # Берем одно состояние из класса эквивалентности
            for state in equivalence_classes[i]:
                # Для каждого символа определим новый переход
                for c in self.Sigma:
                    to_state = self.delta[(state, c)]
                    # Ищем, в каком классе эквивалентности находится состояние, в которое перешли
                    for j in range(len(equivalence_classes)):
                        if to_state in equivalence_classes[j]:
                            new_transition_function[('q' + str(i), c)] = 'q' + str(j)
                            break
                break
        self.delta = new_transition_function

        # Обновление начального состояния
        self.q0 = 'q0'

        # Обновление состояний
        self.Q = set(['q' + str(i) for i in range(len(equivalence_classes))])

        # Обновление финальных состояний
        new_F = set()
        for state in self.F:
            for i in range(len(equivalence_classes)):
                if state in equivalence_classes[i]:
                    new_F.add('q' + str(i))
                    break
        self.F = new_F

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
                line[j + 2] = self.delta[(states[i], symbols[j])]
            # Добавляем в итоговую таблицу
            table.append(line)

        # Запись результатов в файл
        with open(filename, 'w', newline='\n') as f:
            writer_obj = csv.writer(f, delimiter=';')
            writer_obj.writerows(table)


if __name__ == '__main__':
    finite_automaton = FiniteAutomaton()
    finite_automaton.load_transition_function(input_filename)
    finite_automaton.minimize()
    finite_automaton.write_into_file(output_filename)
