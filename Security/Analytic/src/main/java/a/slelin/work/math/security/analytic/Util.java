package a.slelin.work.math.security.analytic;

import lombok.experimental.UtilityClass;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;

/**
 * Вспомогательные функции для матричного шифрования:
 * алфавит, перевод букв в числа и обратно, разбор ввода и красивый вывод матриц.
 * Аннотация {@code @UtilityClass} (Lombok) делает класс финальным, все его члены — статическими,
 * а конструктор — приватным.
 */
@UtilityClass
public class Util {

    /**
     * Русский алфавит из 33 букв (с «Ё»). Буквы Ь, Ы, Ъ стоят в конце — так задано в условии.
     */
    public final String ALPHABET = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЫЪЭЮЯ";

    /**
     * Мощность алфавита (номера букв от 0 до 32).
     */
    public final int N = ALPHABET.length();

    /**
     * Буква, которой текст дополняется до длины, кратной порядку ключа (Ъ, номер 29).
     */
    public final char PAD = 'Ъ';

    // ===================== Алфавит =====================

    /**
     * Номер буквы в алфавите (от 0 до 32) или -1, если такой буквы нет.
     */
    public int indexOf(char letter) {
        return ALPHABET.indexOf(letter);
    }

    /**
     * Буква по номеру. В отличие от шифров замены, номер НЕ приводится по модулю:
     * если число вне диапазона 0…32, значит, ключ или шифротекст неверны.
     */
    public char letterAt(long index) {
        if (index < 0 || index >= N) {
            throw new IllegalArgumentException("Число " + index + " не является номером буквы (0…" + (N - 1) + ").");
        }

        return ALPHABET.charAt((int) index);
    }

    /**
     * Подготовка текста: верхний регистр, удаление пробелов, цифр, знаков препинания и прочих символов.
     */
    public String normalize(String text) {
        if (text == null) {
            return "";
        }

        StringBuilder result = new StringBuilder();
        for (char letter : text.toUpperCase().toCharArray()) {
            if (indexOf(letter) != -1) {
                result.append(letter);
            }
        }

        return result.toString();
    }

    /**
     * Дополнение текста буквой Ъ до длины, кратной n (например, КОД при n = 2 → КОДЪ).
     */
    public String pad(String text, int n) {
        StringBuilder result = new StringBuilder(text);

        while (result.length() % n != 0) {
            result.append(PAD);
        }

        return result.toString();
    }

    /**
     * Отбрасывание букв Ъ в конце расшифрованного текста (они могли появиться из-за дополнения).
     */
    public String unpad(String text) {
        int end = text.length();

        while (end > 0 && text.charAt(end - 1) == PAD) {
            end--;
        }

        return text.substring(0, end);
    }

    /**
     * Перевод текста в последовательность номеров букв (ЗАБАВА → 8 0 1 0 2 0).
     */
    public long[] toNumbers(String text) {
        long[] numbers = new long[text.length()];

        for (int i = 0; i < text.length(); i++) {
            numbers[i] = indexOf(text.charAt(i));
        }

        return numbers;
    }

    /**
     * Перевод номеров букв обратно в текст (8 0 1 0 2 0 → ЗАБАВА).
     */
    public String toText(long[] numbers) {
        StringBuilder result = new StringBuilder();

        for (long number : numbers) {
            result.append(letterAt(number));
        }

        return result.toString();
    }

    /**
     * Разбиение последовательности чисел на блоки (векторы) по n чисел.
     * Длина последовательности должна быть кратна n.
     */
    public List<long[]> blocks(long[] numbers, int n) {
        List<long[]> result = new ArrayList<>();

        for (int start = 0; start < numbers.length; start += n) {
            result.add(Arrays.copyOfRange(numbers, start, start + n));
        }

        return result;
    }

    // ===================== Разбор ввода =====================

    /**
     * Разбор строки целых чисел через пробел (запятые тоже допускаются): "25 19 27" → [25, 19, 27].
     */
    public long[] parseNumbers(String line) {
        if (line == null || line.isBlank()) {
            throw new IllegalArgumentException("Не введено ни одного числа.");
        }

        String[] parts = line.strip().split("[\\s,;]+");
        long[] numbers = new long[parts.length];

        for (int i = 0; i < parts.length; i++) {
            try {
                numbers[i] = Long.parseLong(parts[i]);
            } catch (NumberFormatException e) {
                throw new IllegalArgumentException("'" + parts[i] + "' не является целым числом.");
            }
        }

        return numbers;
    }

    /**
     * Сборка матрицы-ключа из строк, введённых пользователем, с проверкой,
     * что матрица квадратная (n строк по n целых чисел).
     */
    public long[][] parseMatrix(List<String> rows) {
        int n = rows.size();
        long[][] matrix = new long[n][];

        for (int i = 0; i < n; i++) {
            matrix[i] = parseNumbers(rows.get(i));

            if (matrix[i].length != n) {
                throw new IllegalArgumentException("Матрица должна быть квадратной: в строке " + (i + 1)
                        + " ожидалось " + n + " чисел, а введено " + matrix[i].length + ".");
            }
        }

        return matrix;
    }

    /**
     * Проверка, что матрица квадратная и не пустая (на случай, если её собрали в коде, а не ввели).
     */
    public void checkSquare(long[][] matrix) {
        if (matrix == null || matrix.length == 0) {
            throw new IllegalArgumentException("Матрица-ключ пуста.");
        }

        for (long[] row : matrix) {
            if (row == null || row.length != matrix.length) {
                throw new IllegalArgumentException("Матрица-ключ должна быть квадратной.");
            }
        }
    }

    // ===================== Вывод =====================

    /**
     * Числа через пробел: [25, 19, 27] → "25 19 27".
     */
    public String join(long[] numbers) {
        return Arrays.stream(numbers).mapToObj(String::valueOf).collect(Collectors.joining(" "));
    }

    /**
     * Вектор-столбец в строку: [8, 0, 1] → "(8, 0, 1)ᵀ".
     */
    public String vector(long[] numbers) {
        return "(" + Arrays.stream(numbers).mapToObj(String::valueOf).collect(Collectors.joining(", ")) + ")ᵀ";
    }

    /**
     * Целочисленная матрица в виде строк с выровненными столбцами.
     */
    public List<String> matrixLines(long[][] matrix) {
        String[][] cells = new String[matrix.length][];

        for (int i = 0; i < matrix.length; i++) {
            cells[i] = Arrays.stream(matrix[i]).mapToObj(String::valueOf).toArray(String[]::new);
        }

        return matrixLines(cells);
    }

    /**
     * Матрица дробей в виде строк с выровненными столбцами.
     */
    public List<String> matrixLines(LinAlg.Fraction[][] matrix) {
        String[][] cells = new String[matrix.length][];

        for (int i = 0; i < matrix.length; i++) {
            cells[i] = Arrays.stream(matrix[i]).map(LinAlg.Fraction::toString).toArray(String[]::new);
        }

        return matrixLines(cells);
    }

    /**
     * Общая часть вывода матриц: каждое значение выравнивается по правому краю
     * под самое длинное значение матрицы, строка обрамляется вертикальными чертами.
     */
    private List<String> matrixLines(String[][] cells) {
        int width = Arrays.stream(cells).flatMap(Arrays::stream).mapToInt(String::length).max().orElse(1);
        List<String> lines = new ArrayList<>();

        for (String[] row : cells) {
            StringBuilder line = new StringBuilder("│");
            for (String cell : row) {
                line.append(' ').append(" ".repeat(width - cell.length())).append(cell);
            }
            lines.add(line.append(" │").toString());
        }

        return lines;
    }
}
