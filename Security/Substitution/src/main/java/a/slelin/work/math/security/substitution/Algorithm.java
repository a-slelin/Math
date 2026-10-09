package a.slelin.work.math.security.substitution;

/**
 * Шифры замены: Цезаря, Тритемиуса и Вижинера.
 * Каждая функция умеет и шифровать, и расшифровывать (флаг decrypt).
 * Результат возвращается сплошной строкой из заглавных букв без пробелов.
 */
public class Algorithm {

    /**
     * Шифр Цезаря.
     * Шифрование: l = (m + s) mod 32; расшифровка: m = (l − s) mod 32.
     *
     * @param text    исходный текст (будет подготовлен функцией normalize)
     * @param shift   сдвиг — любое целое число (в том числе отрицательное и больше 32)
     * @param decrypt true — расшифровать, false — зашифровать
     */
    public static String caesar(String text, int shift, boolean decrypt) {
        String clean = Util.normalizeText(text);

        // При расшифровке просто сдвигаем в обратную сторону;
        int step = decrypt ? -shift : shift;

        StringBuilder result = new StringBuilder();
        for (char letter : clean.toCharArray()) {
            int m = Util.indexOf(letter);
            result.append(Util.letterAt(m + step));
        }

        return result.toString();
    }

    /**
     * Шифр Тритемиуса со словом-ключом.
     * Под каждой буквой текста записывается буква ключа (ключ повторяется);
     * шифрование: l = (m + k) mod 32; расшифровка: m = (l − k) mod 32.
     *
     * @param text    исходный текст (будет подготовлен функцией normalize)
     * @param key     ключевое слово из русских букв
     * @param decrypt true — расшифровать, false — зашифровать
     */
    public static String trithemius(String text, String key, boolean decrypt) {
        String clean = Util.normalizeText(text);
        String upperKey = Util.normalizeKey(key);

        StringBuilder result = new StringBuilder();
        for (int i = 0; i < clean.length(); i++) {
            int m = Util.indexOf(clean.charAt(i));
            int k = Util.indexOf(upperKey.charAt(i % upperKey.length()));

            int l = decrypt ? m - k : m + k;
            result.append(Util.letterAt(l));
        }

        return result.toString();
    }

    /**
     * Шифр Вижинера через таблицу (а не по формуле).
     * Строится рабочая матрица из строк букв ключа; первая строка таблицы — это алфавит.
     * Шифрование: столбец ищется по букве текста в первой строке,
     * шифробуква стоит на пересечении этого столбца и строки буквы ключа.
     * Расшифровка: в строке буквы ключа ищется шифробуква,
     * над ней в первой строке стоит буква открытого текста.
     *
     * @param text    исходный текст (будет подготовлен функцией normalize)
     * @param key     ключевое слово из русских букв
     * @param decrypt true — расшифровать, false — зашифровать
     */
    public static String vigenere(String text, String key, boolean decrypt) {
        String clean = Util.normalizeText(text);
        String upperKey = Util.normalizeKey(key);
        char[][] matrix = Util.workingMatrix(upperKey);
        char[] firstRow = Util.ALPHABET.toCharArray();

        StringBuilder result = new StringBuilder();
        for (int i = 0; i < clean.length(); i++) {
            char letter = clean.charAt(i);

            // Строка рабочей матрицы, соответствующая текущей букве ключа;
            char[] keyRow = matrix[i % upperKey.length()];

            if (decrypt) {
                int column = findColumn(keyRow, letter);
                result.append(firstRow[column]);
            } else {
                int column = findColumn(firstRow, letter);
                result.append(keyRow[column]);
            }
        }

        return result.toString();
    }

    /**
     * Поиск столбца, в котором в данной строке таблицы стоит нужная буква.
     */
    private static int findColumn(char[] row, char letter) {
        for (int column = 0; column < row.length; column++) {
            if (row[column] == letter) {
                return column;
            }
        }

        throw new IllegalStateException("Буква '" + letter + "' не найдена в строке таблицы.");
    }
}
