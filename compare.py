import ast


class Visitor(ast.NodeVisitor):
    def visit(self, node: ast.AST) -> None:
        if isinstance(node, ast.Name):
            # Заменяет любые имена переменных на 'a'
            node.id = 'a'

        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
            # Если docstrings, то заменяет константу на пустую
            result = ast.Constant
            ast.copy_location(node.value, result)
            node.value = result

        elif isinstance(node, ast.FunctionDef):
            # Заменяет имена аргументов функции на 'a'
            for i in range(len(node.args.args)):
                result = ast.arg('a')
                ast.copy_location(node.args.args[i], result)
                node.args.args[i] = result
            # Заменяет имя функции на 'a'
            node.name = 'a'
            # Очищает декораторы и удаляет аннотации
            node.decorator_list = []
            del node.returns

        self.generic_visit(node)


# Реализация расстояния Левенштейна с помощью техники динамического программирования
def editDistance(string1: str, string2: str) -> int:
    matrix = [[0] * (len(string2) + 1) for _ in range(len(string1) + 1)]
    for j in range(len(string2) + 1):
        matrix[0][j] = j
    for i in range(len(string1) + 1):
        matrix[i][0] = i
    for i in range(1, len(string1) + 1):
        for j in range(1, len(string2) + 1):
            matrix[i][j] = min(matrix[i][j - 1] + 1,
                               matrix[i - 1][j] + 1,
                               matrix[i - 1][j - 1] + (0 if string1[i - 1] == string2[j - 1] else 1))
    return matrix[-1][-1]


# compare нормализует оба текста, а затем возвращает их коэффициент совпадения
def compare(filename1: str, filename2: str) -> float:
    text1 = open(filename1, mode="r", encoding="utf-8").read()
    text2 = open(filename2, mode="r", encoding="utf-8").read()

    # Не все документы поддаются парсингу из-за импортируемых синтаксических конструкций, которые ast.parse
    # не может распознать. В таких случаях можно просто не нормализовывать файл.
    try:
        # Преобразование текстов в абстрактные синтаксические деревья
        ast1 = ast.parse(text1, type_comments=False)
        ast2 = ast.parse(text2, type_comments=False)

        # Посещение каждого узла, нормализация
        Visitor().visit(ast1)
        Visitor().visit(ast2)

        # Преобразование дерева обратно в код, но уже нормализованный
        transformedText1 = ast.unparse(ast1)
        transformedText2 = ast.unparse(ast2)

        # Возвращается расстояние Левенштейна от двух текстов, поделенное на большее из двух чисел:
        # 1) разность длин нормализованных текстов; 2) длина нормализованного текста №2
        # Таким образом, коэффициент совпадения не превышает 1
        return editDistance(transformedText1, transformedText2) / \
            max(abs(len(transformedText1) - len(transformedText2)), len(transformedText2))

    except:
        # Возвращается коэффициент совпадения, но для ненормализованных текстов
        return editDistance(text1, text2) / max(abs(len(text1) - len(text2)), len(text2))


# solve сравнивает каждую пару файлов из [input file] и загружает коэффициент совпадения в [output file]
def solve(inputFile: str, outputFile: str) -> None:
    input = open(inputFile, mode="r", encoding="utf-8")
    output = open(outputFile, mode="w", encoding="utf-8")

    # Пробегается по всем парам файлов
    files = input.read().split()
    for i in range(0, len(files), 2):
        file1 = files[i]
        file2 = files[i + 1]

        # Запись округленного до 3-х знаков результата в [output file]
        print(round(compare(file1, file2), 3), file=output)


def main():
    # Запрос имён файлов ввода и вывода
    inputFile = input()
    outputFile = input()
    solve(inputFile, outputFile)


if __name__ == '__main__':
    main()
