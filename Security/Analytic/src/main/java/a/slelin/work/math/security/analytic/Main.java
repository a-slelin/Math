package a.slelin.work.math.security.analytic;

import java.nio.charset.Charset;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;
import java.util.Scanner;

/**
 * Консольный интерфейс: меню, ввод ключа и текста, красивый вывод результатов и промежуточных вычислений.
 * Шифрование — в классе {@link Decoder}, линейная алгебра — в {@link LinAlg}, вспомогательное — в {@link Util}.
 */
public class Main {

    /**
     * Ширина рамок в консоли.
     */
    public static final int WIDTH = 50;

    /**
     * Слово для демонстрации сгенерированного ключа (дополнительное задание варианта 2).
     */
    public static final String DEMO_WORD = "ВАРИАНТ";

    /**
     * Чтение с консоли в её родной кодировке.
     */
    public static final Scanner in = new Scanner(System.in,
            Charset.forName(System.getProperty("stdin.encoding", Charset.defaultCharset().name())));

    /**
     * Текущая матрица-ключ (null, пока пользователь её не ввёл).
     */
    static long[][] key = null;

    /**
     * Режим вывода промежуточных результатов (номера букв, блоки, обратная матрица).
     */
    static boolean verbose = true;

    static void main() {
        while (true) {
            printMenu();
            String choice = ask("Выберите пункт");

            try {
                switch (choice) {
                    case "1" -> runInputKey();
                    case "2" -> runEncrypt();
                    case "3" -> runDecrypt();
                    case "4" -> runInverse();
                    case "5" -> runGenerate();
                    case "6" -> {
                        verbose = !verbose;
                        System.out.println("Подробный вывод " + (verbose ? "включён." : "выключен."));
                    }
                    case "0" -> {
                        System.out.println("До свидания!");
                        return;
                    }
                    default -> printError("Нет такого пункта меню: '" + choice + "'.");
                }
            } catch (IllegalArgumentException | ArithmeticException e) {
                // Ошибки ввода и проверок (вырожденный ключ, неверный шифротекст, переполнение);
                printError(e.getMessage());
            }
        }
    }

    // ===================== Пункты меню =====================

    /**
     * Ввод матрицы-ключа: порядок n и n строк по n целых чисел. Вырожденный ключ не сохраняется.
     */
    static void runInputKey() {
        int n = askOrder("Порядок матрицы n");

        System.out.println("Введите " + n + " строки по " + n + " целых чисел через пробел:");
        List<String> rows = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            rows.add(ask("  строка " + (i + 1)));
        }

        long[][] matrix = Util.parseMatrix(rows);
        long det = LinAlg.det(matrix);

        System.out.println();
        printMatrix("A", Util.matrixLines(matrix));
        System.out.println("det = " + det);

        // Проверка det ≠ 0 и понятное сообщение об ошибке;
        Decoder.checkKey(matrix);

        key = matrix;
        System.out.println("Ключ сохранён.");
    }

    /**
     * Шифрование текста текущим ключом.
     */
    static void runEncrypt() {
        requireKey();
        String text = ask("Текст");

        long[] cipher = Decoder.encrypt(text, key);

        if (verbose) {
            String padded = Util.pad(Util.normalize(text), key.length);
            long[] numbers = Util.toNumbers(padded);

            System.out.println();
            System.out.println("Текст:  " + padded);
            System.out.println("Номера: " + Util.join(numbers));
            printBlocks("B", Util.blocks(numbers, key.length), "C", Util.blocks(cipher, key.length));
        }

        printResult("Шифротекст: " + Util.join(cipher));
    }

    /**
     * Расшифровка чисел текущим ключом.
     */
    static void runDecrypt() {
        requireKey();
        long[] cipher = Util.parseNumbers(ask("Числа"));

        String text = Decoder.decrypt(cipher, key);

        if (verbose) {
            System.out.println();
            printInverse(key);
            printBlocks("C", Util.blocks(cipher, key.length), "B", Util.blocks(Util.toNumbers(text), key.length));
        }

        printResult("Текст: " + withoutPad(text));
    }

    /**
     * Промежуточные результаты для текущего ключа:
     * определитель, алгебраические дополнения, транспонирование, обратная матрица и проверка A · A⁻¹ = E.
     */
    static void runInverse() {
        requireKey();

        System.out.println();
        printMatrix("A", Util.matrixLines(key));
        printInverse(key);

        boolean identity = LinAlg.isIdentity(LinAlg.multiply(key, LinAlg.inverse(key)));
        System.out.println("Проверка A · A⁻¹ = E: " + (identity ? "верно ✔" : "НЕВЕРНО ✘"));
    }

    /**
     * Дополнительное задание: генерация случайного ключа с det = ±1,
     * у которого обратная матрица тоже целочисленная, и демонстрация на слове ВАРИАНТ.
     */
    static void runGenerate() {
        int n = askOrder("Порядок матрицы n (2, 3, 4, …)");
        long[][] generated = LinAlg.randomUnimodular(n, new Random());
        long[][] inverse = LinAlg.toLong(LinAlg.inverse(generated));

        System.out.println();
        printMatrix("K", Util.matrixLines(generated));
        System.out.println("det = " + LinAlg.det(generated));
        printMatrix("K⁻¹", Util.matrixLines(inverse));

        String word = ask("Слово (Enter — " + DEMO_WORD + ")");
        if (word.isBlank()) {
            word = DEMO_WORD;
        }

        long[] cipher = Decoder.encrypt(word, generated);
        String text = Decoder.decrypt(cipher, generated);

        printResult("Шифротекст: " + Util.join(cipher), "Расшифровка: " + withoutPad(text));

        if (ask("Сделать этот ключ текущим? (y/n)").equalsIgnoreCase("y")) {
            key = generated;
            System.out.println("Ключ сохранён.");
        }
    }

    // ===================== Ввод =====================

    /**
     * Вопрос пользователю и чтение одной строки ответа.
     */
    static String ask(String question) {
        System.out.print(question + ": ");

        if (!in.hasNextLine()) {
            // Ввод закончился (например, Ctrl+D) — просто выходим;
            System.out.println();
            System.exit(0);
        }

        return in.nextLine().strip();
    }

    /**
     * Ввод порядка матрицы — целого числа не меньше 2.
     */
    static int askOrder(String question) {
        String answer = ask(question);

        try {
            int n = Integer.parseInt(answer);
            if (n < 2) {
                throw new IllegalArgumentException("Порядок матрицы должен быть не меньше 2.");
            }
            return n;
        } catch (NumberFormatException e) {
            throw new IllegalArgumentException("Порядок матрицы должен быть целым числом, а не '" + answer + "'.");
        }
    }

    /**
     * Проверка, что ключ уже введён.
     */
    static void requireKey() {
        if (key == null) {
            throw new IllegalArgumentException("Сначала введите матрицу-ключ (пункт 1) или сгенерируйте её (пункт 5).");
        }
    }

    // ===================== Вывод =====================

    /**
     * Главное меню в рамке; внизу показан порядок текущего ключа и режим вывода.
     */
    static void printMenu() {
        String status = (key == null ? "  Ключ не задан" : "  Ключ: матрица " + key.length + "×" + key.length)
                + ", подробно: " + (verbose ? "вкл" : "выкл");

        System.out.println();
        System.out.println("╔" + "═".repeat(WIDTH) + "╗");
        System.out.println(boxLine(center("Матричное шифрование")));
        System.out.println("╠" + "═".repeat(WIDTH) + "╣");
        System.out.println(boxLine("  1. Ввести матрицу-ключ"));
        System.out.println(boxLine("  2. Зашифровать текст"));
        System.out.println(boxLine("  3. Расшифровать числа"));
        System.out.println(boxLine("  4. Показать определитель и обратную матрицу"));
        System.out.println(boxLine("  5. Сгенерировать ключ с det = ±1"));
        System.out.println(boxLine("  6. Подробный вывод (вкл/выкл)"));
        System.out.println(boxLine("  0. Выход"));
        System.out.println("╠" + "═".repeat(WIDTH) + "╣");
        System.out.println(boxLine(status));
        System.out.println("╚" + "═".repeat(WIDTH) + "╝");
    }

    /**
     * Схема нахождения обратной матрицы (п. 2.3): Δ → A* → (A*)ᵀ → A⁻¹ = (1/Δ) · (A*)ᵀ.
     */
    static void printInverse(long[][] matrix) {
        long det = LinAlg.det(matrix);
        long[][] cofactors = LinAlg.cofactors(matrix);

        System.out.println("Δ = det A = " + det);
        printMatrix("A*", Util.matrixLines(cofactors));
        printMatrix("(A*)ᵀ", Util.matrixLines(LinAlg.transpose(cofactors)));
        printMatrix("A⁻¹", Util.matrixLines(LinAlg.inverse(matrix)));
    }

    /**
     * Матрица с подписью слева на средней строке:
     * <pre>
     *       │ 3 2 1 │
     *   A = │ 2 5 3 │
     *       │ 3 4 3 │
     * </pre>
     */
    static void printMatrix(String name, List<String> lines) {
        String label = name + " = ";
        String indent = " ".repeat(label.length());
        int middle = (lines.size() - 1) / 2;

        for (int i = 0; i < lines.size(); i++) {
            System.out.println("  " + (i == middle ? label : indent) + lines.get(i));
        }
    }

    /**
     * Соответствие блоков: B₁ = (8, 0, 1)ᵀ → C₁ = (25, 19, 27)ᵀ.
     */
    static void printBlocks(String from, List<long[]> source, String to, List<long[]> target) {
        for (int k = 0; k < source.size(); k++) {
            System.out.println("  " + from + (k + 1) + " = " + Util.vector(source.get(k))
                    + "  →  " + to + (k + 1) + " = " + Util.vector(target.get(k)));
        }
    }

    /**
     * Результат в рамке (одна или несколько строк). Если текст длинный, рамка расширяется под него.
     */
    static void printResult(String... lines) {
        int width = WIDTH;
        for (String line : lines) {
            width = Math.max(width, line.length() + 2);
        }

        System.out.println();
        System.out.println("┌" + "─".repeat(width) + "┐");
        for (String line : lines) {
            System.out.println("│" + padRight(" " + line, width) + "│");
        }
        System.out.println("└" + "─".repeat(width) + "┘");
    }

    /**
     * Расшифрованный текст и, если в конце есть дополняющие буквы Ъ, — он же без них.
     */
    static String withoutPad(String text) {
        String clean = Util.unpad(text);
        return clean.equals(text) ? text : text + "  (без Ъ: " + clean + ")";
    }

    /**
     * Сообщение об ошибке.
     */
    static void printError(String message) {
        System.out.println();
        System.out.println("[Ошибка] " + message);
    }

    /**
     * Строка внутри рамки, дополненная пробелами до нужной ширины.
     */
    static String boxLine(String text) {
        return "║" + padRight(text, WIDTH) + "║";
    }

    /**
     * Текст, дополненный справа пробелами до нужной ширины.
     */
    static String padRight(String text, int width) {
        return text + " ".repeat(Math.max(0, width - text.length()));
    }

    /**
     * Текст по центру строки шириной WIDTH.
     */
    static String center(@SuppressWarnings("SameParameterValue") String text) {
        int left = Math.max(0, (WIDTH - text.length()) / 2);
        return " ".repeat(left) + text;
    }
}
