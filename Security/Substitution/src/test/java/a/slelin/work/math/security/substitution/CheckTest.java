package a.slelin.work.math.security.substitution;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.MethodOrderer;
import org.junit.jupiter.api.Order;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestMethodOrder;

import static org.junit.jupiter.api.Assertions.assertEquals;

/**
 * Проверка ручного решения (часть А) для варианта 2.
 */
@DisplayName("Проверка ручного решения (часть А), вариант 2")
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
public class CheckTest {

    // ===================== Задание 1 =====================

    @Test
    @Order(1)
    @DisplayName("Задание 1. Цезарь, расшифровка: УТИХЦДСТЖОД со сдвигом 4 → ПОДСТАНОВКА")
    void task1CaesarDecrypt() {
        // УТИХЦДСТЖОД, сдвиг 4;
        assertEquals("ПОДСТАНОВКА", Algorithm.caesar("УТИХЦДСТЖОД", 4, true));
    }

    // ===================== Задание 2 =====================

    @Test
    @Order(2)
    @DisplayName("Задание 2. Цезарь, шифрование: ИНФОРМАЦИЯ со сдвигом 7 → ПФЫХЧУЗЭПЖ")
    void task2CaesarEncrypt() {
        // ИНФОРМАЦИЯ, сдвиг 7;
        assertEquals("ПФЫХЧУЗЭПЖ", Algorithm.caesar("ИНФОРМАЦИЯ", 7, false));
    }

    // ===================== Задание 3 =====================

    @Test
    @Order(3)
    @DisplayName("Задание 3А. Тритемиус, шифрование: ВСТРЕЧА В ПОЛДЕНЬ с ключом ЛУНА")
    void task3aTrithemiusEncrypt() {
        String result = Algorithm.trithemius("ВСТРЕЧА В ПОЛДЕНЬ", "ЛУНА", false);

        assertEquals("НДЯРР КНВЬБ ШДРАЗ", Util.groupByFive(result));
    }

    @Test
    @Order(4)
    @DisplayName("Задание 3Б. Тритемиус, шифрование: ШИФР ЦЕЗАРЯ ЛЕГКО ВЗЛОМАТЬ с ключом БАХ")
    void task3bTrithemiusEncrypt() {
        String result = Algorithm.trithemius("ШИФР ЦЕЗАРЯ ЛЕГКО ВЗЛОМАТЬ", "БАХ", false);

        assertEquals("ЩИЙСЦ ЬИАЕА ЛЬДКГ ГЗАПМ ХУЬ", Util.groupByFive(result));
    }

    // ===================== Задание 4 =====================

    @Test
    @Order(5)
    @DisplayName("Задание 4. Вижинер, шифрование: ДОСТАВКА ТОВАРА ПРОИЗВЕДЕНА ВОВРЕМЯ с ключом ГОРОД")
    void task4VigenereEncrypt() {
        String result = Algorithm.vigenere("ДОСТАВКА ТОВАРА ПРОИЗВЕДЕНА ВОВРЕМЯ", "ГОРОД", false);

        // Первое слово дано в условии: ДОСТАВКА → ЗЪБАДЕШР;
        assertEquals("ЗЪБАДЕШР", result.substring(0, 8));
        assertEquals("ЗЪБАД ЕШРАТ ЕОАОУ УЪШХЖ ИТХЫД ЕЪТЮЙ ПН", Util.groupByFive(result));
    }

    // ===================== Задание 5 =====================

    @Test
    @Order(6)
    @DisplayName("Задание 5. Вижинер, шифрование: НАДЕЖНЫЙ ПАРОЛЬ ... с ключом ШОПЕН")
    void task5VigenereEncrypt() {
        String text = "НАДЕЖНЫЙ ПАРОЛЬ СОДЕРЖИТ НЕ МЕНЕЕ ДВЕНАДЦАТИ СИМВОЛОВ";
        String result = Algorithm.vigenere(text, "ШОПЕН", false);

        assertEquals("ЕОУКУ ЕЙШФН ИЪЬЯЮ ЖТФХУ ААЪКЩ ЭЫФКС ЬУЪЕС ООБНЮ АЬСУШ ЖР", Util.groupByFive(result));
    }

    // ===================== Задание 6 =====================

    @Test
    @Order(7)
    @DisplayName("Задание 6А. Вижинер, расшифровка с ключом МИР → АУТЕНТИФИКАЦИЯ")
    void task6aVigenereDecrypt() {
        assertEquals("АУТЕНТИФИКАЦИЯ", Algorithm.vigenere("МЫВСХ ВФЪШЦ ИЖФЗ", "МИР", true));
    }

    @Test
    @Order(8)
    @DisplayName("Задание 6Б. Вижинер, расшифровка с ключом СЕЙФ → ЗАЩИТА ОТ УТЕЧЕК ДАННЫХ")
    void task6bVigenereDecrypt() {
        assertEquals("ЗАЩИТАОТУТЕЧЕКДАННЫХ", Algorithm.vigenere("ШЕВЪГ ЕЧЖДЧ ОЛЦПН ФЮТДЙ", "СЕЙФ", true));
    }

    @Test
    @Order(9)
    @DisplayName("Задание 6В. Вижинер, расшифровка с ключом ПАРОЛЬ → ИНФОРМАЦИЯ ЯВЛЯЕТСЯ ...")
    void task6cVigenereDecrypt() {
        String cipher = "ЧНДЪЫ ЖПЦШН КЪЬЯХ АЪЩЭД ЭЦЧВЦ ВРФШЯ ШШШГЛ ДБИТЪ НИЯГР ЫУБПЦ ШЦ";

        // Информация является одним из важнейших активов организации;
        assertEquals("ИНФОРМАЦИЯЯВЛЯЕТСЯОДНИМИЗВАЖНЕЙШИХАКТИВОВОРГАНИЗАЦИИ",
                Algorithm.vigenere(cipher, "ПАРОЛЬ", true));
    }

    // ===================== Обратная проверка =====================

    @Test
    @Order(10)
    @DisplayName("Обратная проверка: расшифровка зашифрованного текста возвращает исходный")
    void encryptThenDecrypt() {
        // Расшифровка зашифрованного текста возвращает исходный текст;
        String text = "НАДЕЖНЫЙПАРОЛЬ";

        assertEquals(text, Algorithm.caesar(Algorithm.caesar(text, 7, false), 7, true));
        assertEquals(text, Algorithm.trithemius(Algorithm.trithemius(text, "БАХ", false), "БАХ", true));
        assertEquals(text, Algorithm.vigenere(Algorithm.vigenere(text, "ШОПЕН", false), "ШОПЕН", true));
    }
}
