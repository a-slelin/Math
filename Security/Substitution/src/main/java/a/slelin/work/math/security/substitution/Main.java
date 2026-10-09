package a.slelin.work.math.security.substitution;

import java.io.IOException;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Scanner;

/**
 * Консольный интерфейс: меню, ввод текста и ключа, вывод результата.
 * Сами шифры находятся в классе Algorithm, вспомогательные функции — в классе Util.
 */
public class Main {

    /**
     * Ширина рамок в консоли.
     */
    public static final int WIDTH = 50;

    /**
     * Файл, в который сохраняется таблица Вижинера.
     */
    public static final String TABLE_FILE = "vigenere_table.txt";

    /**
     * Чтение с консоли в её родной кодировке.
     */
    public static final Scanner in = new Scanner(System.in,
            Charset.forName(System.getProperty("stdin.encoding", Charset.defaultCharset().name())));

    static void main() {
        while (true) {
            printMenu();
            String choice = ask("Выберите пункт");

            try {
                switch (choice) {
                    case "1" -> runCaesar();
                    case "2" -> runTrithemius();
                    case "3" -> runVigenere();
                    case "4" -> runTable();
                    case "0" -> {
                        System.out.println("До свидания!");
                        return;
                    }
                    default -> printError("Нет такого пункта меню: '" + choice + "'.");
                }
            } catch (IllegalArgumentException e) {
                // Ошибки ввода (пустой ключ, посторонние символы, нечисловой сдвиг);
                printError(e.getMessage());
            }
        }
    }

    // ===================== Пункты меню =====================

    /**
     * Шифр Цезаря: ввод режима, текста и сдвига.
     */
    static void runCaesar() {
        boolean decrypt = askMode();
        String text = ask("Введите текст");
        int shift = Util.parseShift(ask("Сдвиг"));

        String result = Algorithm.caesar(text, shift, decrypt);
        printResult(result);
    }

    /**
     * Шифр Тритемиуса: ввод режима, текста и ключевого слова.
     */
    static void runTrithemius() {
        boolean decrypt = askMode();
        String text = ask("Введите текст");
        String key = ask("Ключ");

        String result = Algorithm.trithemius(text, key, decrypt);
        printKeyUnderText(text, key);
        printResult(result);
    }

    /**
     * Шифр Вижинера: ввод режима, текста и ключевого слова.
     */
    static void runVigenere() {
        boolean decrypt = askMode();
        String text = ask("Введите текст");
        String key = ask("Ключ");

        String result = Algorithm.vigenere(text, key, decrypt);
        printKeyUnderText(text, key);
        printResult(result);
    }

    /**
     * Дополнительное задание: вывод таблицы Вижинера 32×32
     * и рабочей матрицы для произвольного ключа (в консоль и при желании в файл).
     */
    static void runTable() {
        String key = Util.normalizeKey(ask("Ключ"));

        String table = tableToString("Таблица Вижинера 32×32", Util.vigenereTable(), null);
        String matrix = tableToString("Рабочая матрица для ключа " + key, Util.workingMatrix(key), key);

        System.out.println();
        System.out.print(table);
        System.out.println();
        System.out.print(matrix);

        String save = ask("Сохранить в файл " + TABLE_FILE + "? (y/n)");
        if (save.equalsIgnoreCase("y")) {
            try {
                Path path = Path.of(TABLE_FILE);
                Files.writeString(path, table + System.lineSeparator() + matrix);
                System.out.println("Файл сохранён: " + path.toAbsolutePath());
            } catch (IOException e) {
                printError("Не удалось сохранить файл: " + e.getMessage());
            }
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
     * Выбор режима: e — зашифровать, d — расшифровать. Спрашиваем, пока не получим верный ответ.
     */
    static boolean askMode() {
        while (true) {
            String mode = ask("Режим (e - зашифровать, d - расшифровать)");

            if (mode.equalsIgnoreCase("e")) {
                return false;
            }
            if (mode.equalsIgnoreCase("d")) {
                return true;
            }

            printError("Введите 'e' или 'd'.");
        }
    }

    // ===================== Вывод =====================

    /**
     * Главное меню в рамке.
     */
    static void printMenu() {
        System.out.println();
        System.out.println("╔" + "═".repeat(WIDTH) + "╗");
        System.out.println(boxLine(center("Классические шифры замены")));
        System.out.println("╠" + "═".repeat(WIDTH) + "╣");
        System.out.println(boxLine("  1. Шифр Цезаря"));
        System.out.println(boxLine("  2. Шифр Тритемиуса"));
        System.out.println(boxLine("  3. Шифр Вижинера"));
        System.out.println(boxLine("  4. Таблица Вижинера"));
        System.out.println(boxLine("  0. Выход"));
        System.out.println("╚" + "═".repeat(WIDTH) + "╝");
    }

    /**
     * Подготовленный текст и ключ, записанный под ним (как при ручном решении).
     */
    static void printKeyUnderText(String text, String key) {
        String clean = Util.normalize(text);
        String upperKey = Util.normalizeKey(key);

        System.out.println();
        System.out.println("Текст: " + Util.groupByFive(clean));
        System.out.println("Ключ:  " + Util.groupByFive(Util.repeatKey(upperKey, clean.length())));
    }

    /**
     * Результат: группами по 5 знаков и сплошной строкой.
     */
    static void printResult(String result) {
        System.out.println();
        System.out.println("┌" + "─".repeat(WIDTH) + "┐");
        System.out.println("│ Результат: " + Util.groupByFive(result));
        System.out.println("│ Сплошной:  " + result);
        System.out.println("└" + "─".repeat(WIDTH) + "┘");
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
        return "║" + text + " ".repeat(Math.max(0, WIDTH - text.length())) + "║";
    }

    /**
     * Текст по центру строки шириной WIDTH.
     */
    static String center(String text) {
        int left = Math.max(0, (WIDTH - text.length()) / 2);
        return " ".repeat(left) + text;
    }

    /**
     * Таблица с заголовками: сверху — буквы открытого текста (алфавит),
     * слева — первая буква строки (для рабочей матрицы — буква ключа, первая строка помечена «*»).
     */
    static String tableToString(String title, char[][] matrix, String key) {
        String line = System.lineSeparator();
        StringBuilder result = new StringBuilder();

        result.append(title).append(line);

        // Заголовок со столбцами;
        result.append("    │");
        for (int column = 0; column < Util.N; column++) {
            result.append(' ').append(Util.letterAt(column));
        }
        result.append(line);
        result.append("────┼").append("──".repeat(Util.N)).append(line);

        // Строки таблицы;
        for (int row = 0; row < matrix.length; row++) {
            String label;
            if (key == null) {
                label = String.valueOf(matrix[row][0]);
            } else {
                label = row == 0 ? "*" : String.valueOf(key.charAt(row - 1));
            }

            result.append("  ").append(label).append(" │");
            for (char letter : matrix[row]) {
                result.append(' ').append(letter);
            }
            result.append(line);
        }

        return result.toString();
    }
}
