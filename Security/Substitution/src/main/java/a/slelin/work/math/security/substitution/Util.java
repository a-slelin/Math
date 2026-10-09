package a.slelin.work.math.security.substitution;

/**
 * Вспомогательные функции для шифров замены:
 * работа с алфавитом, подготовка текста и ключа, построение таблицы Вижинера.
 */
public final class Util {

    /**
     * Русский алфавит из 32 букв (без «Ё»).
     */
    public static final String ALPHABET = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЫЪЭЮЯ";

    /**
     * Мощность алфавита (модуль для всех вычислений).
     */
    public static final int N = ALPHABET.length();

    /**
     * Размер группы символов при выводе шифротекста.
     */
    public static final int GROUP_SIZE = 5;

    /**
     * Номер буквы в алфавите (от 0 до 31) или -1, если такой буквы нет.
     */
    public static int indexOf(char letter) {
        return ALPHABET.indexOf(letter);
    }

    /**
     * Буква по номеру. Номер приводится по модулю 32, поэтому подходит любое целое число.
     */
    public static char letterAt(int index) {
        return ALPHABET.charAt(mod(index));
    }

    /**
     * Остаток от деления на 32, всегда неотрицательный (например, -1 → 31).
     */
    public static int mod(int value) {
        return ((value % N) + N) % N;
    }

    /**
     * Подготовка текста: верхний регистр, «Ё» → «Е»,
     * удаление пробелов, цифр, знаков препинания и прочих символов.
     */
    public static String normalize(String text) {
        if (text == null) {
            return "";
        }

        String upper = text.toUpperCase().replace('Ё', 'Е');
        StringBuilder result = new StringBuilder();

        for (char letter : upper.toCharArray()) {
            if (indexOf(letter) != -1) {
                result.append(letter);
            }
        }

        return result.toString();
    }

    /**
     * Проверка и подготовка ключевого слова.
     * Ключ не должен быть пустым и может состоять только из русских букв.
     */
    public static String normalizeKey(String key) {
        if (key == null || key.isBlank()) {
            throw new IllegalArgumentException("Ключ не может быть пустым.");
        }

        String upper = key.strip().toUpperCase().replace('Ё', 'Е');

        for (char letter : upper.toCharArray()) {
            if (indexOf(letter) == -1) {
                throw new IllegalArgumentException(
                        "Ключ может содержать только русские буквы, найден посторонний символ: '" + letter + "'.");
            }
        }

        return upper;
    }

    /**
     * Проверка текста: после подготовки в нём должна остаться хотя бы одна буква.
     */
    public static String normalizeText(String text) {
        String result = normalize(text);

        if (result.isEmpty()) {
            throw new IllegalArgumentException("Текст не содержит ни одной русской буквы.");
        }

        return result;
    }

    /**
     * Перевод строки со сдвигом в целое число (допускаются отрицательные и большие числа).
     */
    public static int parseShift(String shift) {
        if (shift == null || shift.isBlank()) {
            throw new IllegalArgumentException("Сдвиг не может быть пустым.");
        }

        try {
            return Integer.parseInt(shift.strip());
        } catch (NumberFormatException e) {
            throw new IllegalArgumentException("Сдвиг должен быть целым числом, а не '" + shift.strip() + "'.");
        }
    }

    /**
     * Построение полной таблицы Вижинера 32×32.
     * Каждая строка — алфавит, циклически сдвинутый на номер строки.
     */
    public static char[][] vigenereTable() {
        char[][] table = new char[N][N];

        for (int row = 0; row < N; row++) {
            for (int column = 0; column < N; column++) {
                table[row][column] = letterAt(row + column);
            }
        }

        return table;
    }

    /**
     * Рабочая матрица шифрования (правило 1): первая строка таблицы (алфавит)
     * и строки, начинающиеся с букв ключа, в порядке следования букв в ключе.
     * Строка с номером i + 1 соответствует i-й букве ключа.
     */
    public static char[][] workingMatrix(String key) {
        String upperKey = normalizeKey(key);
        char[][] table = vigenereTable();
        char[][] matrix = new char[upperKey.length() + 1][];

        // Первая строка — обычный алфавит;
        matrix[0] = table[0];

        // Остальные строки выбираются по первой букве (она совпадает с номером строки);
        for (int i = 0; i < upperKey.length(); i++) {
            matrix[i + 1] = table[indexOf(upperKey.charAt(i))];
        }

        return matrix;
    }

    /**
     * Разбиение текста на группы по 5 знаков через пробел.
     */
    public static String groupByFive(String text) {
        StringBuilder result = new StringBuilder();

        for (int i = 0; i < text.length(); i++) {
            if (i > 0 && i % GROUP_SIZE == 0) {
                result.append(' ');
            }
            result.append(text.charAt(i));
        }

        return result.toString();
    }

    /**
     * Ключ, записанный под текстом с повторением (например, ГОРОДГОРОДГ...).
     */
    public static String repeatKey(String key, int length) {
        StringBuilder result = new StringBuilder();

        for (int i = 0; i < length; i++) {
            result.append(key.charAt(i % key.length()));
        }

        return result.toString();
    }
}
