package a.slelin.work.math.security.substitution;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.MethodOrderer;
import org.junit.jupiter.api.Order;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestMethodOrder;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

@DisplayName("Базовые тесты")
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
public class BasicTest {

    // Базовые тесты

    @Test
    @Order(1)
    @DisplayName("Цезарь, шифрование: АЛФАВИТ со сдвигом 3")
    void caesarEncryptAlphabet() {
        assertEquals("ГОЧГЕЛХ", Algorithm.caesar("АЛФАВИТ", 3, false));
    }

    @Test
    @Order(2)
    @DisplayName("Цезарь, шифрование: ЯБЛОКО со сдвигом 1")
    void caesarEncryptApple() {
        assertEquals("АВМПЛП", Algorithm.caesar("ЯБЛОКО", 1, false));
    }

    @Test
    @Order(3)
    @DisplayName("Цезарь, шифрование: ЭЮЯ со сдвигом 3")
    void caesarEncryptEndOfAlphabet() {
        assertEquals("АБВ", Algorithm.caesar("ЭЮЯ", 3, false));
    }

    @Test
    @Order(4)
    @DisplayName("Цезарь, расшифровка: ГОЧГЕЛХ со сдвигом 3")
    void caesarDecryptAlphabet() {
        assertEquals("АЛФАВИТ", Algorithm.caesar("ГОЧГЕЛХ", 3, true));
    }

    @Test
    @Order(5)
    @DisplayName("Тритемиус, шифрование: ПРИВЕТ с ключом ЗАПИСЬ")
    void trithemiusEncryptHello() {
        assertEquals("ЦРЧКЦМ", Algorithm.trithemius("ПРИВЕТ", "ЗАПИСЬ", false));
    }

    @Test
    @Order(6)
    @DisplayName("Вижинер, шифрование: ГРУЗИТЕ с ключом ВЕНТИЛЬ")
    void vigenereEncryptLoad() {
        assertEquals("ЕХАЩРЭЯ", Algorithm.vigenere("ГРУЗИТЕ", "ВЕНТИЛЬ", false));
    }

    @Test
    @Order(7)
    @DisplayName("Вижинер, расшифровка: ЕХАЩРЭЯ с ключом ВЕНТИЛЬ")
    void vigenereDecryptLoad() {
        assertEquals("ГРУЗИТЕ", Algorithm.vigenere("ЕХАЩРЭЯ", "ВЕНТИЛЬ", true));
    }

    // Тесты из теории

    @Test
    @Order(8)
    @DisplayName("Тритемиус: полный пример из теории (ключ ЗАПИСЬ)")
    void trithemiusExampleFromTheory() {
        String text = "В связи с создавшимся положением отодвигаем сроки возвращения домой Рамзай";
        String expected = "ЙССЗШ ВШСЭП ХЬЙШЧ ФВЩЦО ЬЦЧЯФ ИФФЯМ ХДСРФ ЬММАШ ЯДПВЭ ПУКЗЩ ФХЩЩЛ ОЫЦЬК ЗМЦИЬ";

        assertEquals(expected, Util.groupByFive(Algorithm.trithemius(text, "ЗАПИСЬ", false)));
    }

    @Test
    @Order(9)
    @DisplayName("Вижинер: полный пример из теории (ГРУЗИТЕ АПЕЛЬСИНЫ БОЧКАМИ, ключ ВЕНТИЛЬ)")
    void vigenereExampleFromTheory() {
        String expected = "ЕХАЩР ЭЯВФТ ЭВЪВП АОАЯХ ЬОН";

        assertEquals(expected, Util.groupByFive(Algorithm.vigenere("ГРУЗИТЕ АПЕЛЬСИНЫ БОЧКАМИ", "ВЕНТИЛЬ", false)));
    }

    // Тесты на проверку условий пункта 4.1

    @Test
    @Order(10)
    @DisplayName("Подготовка текста: регистр, замена «ё» на «е», удаление пробелов, цифр и знаков")
    void normalizeRemovesExtraSymbols() {
        assertEquals("ЕЛКАЕЖИК", Util.normalize("Ёлка, ёжик! 123"));
    }

    @Test
    @Order(11)
    @DisplayName("Цезарь: отрицательный сдвиг и сдвиг больше 32")
    void caesarNegativeAndBigShift() {
        assertEquals("ГОЧГЕЛХ", Algorithm.caesar("АЛФАВИТ", 35, false));
        assertEquals("ГОЧГЕЛХ", Algorithm.caesar("АЛФАВИТ", -29, false));
    }

    @Test
    @Order(12)
    @DisplayName("Тритемиус по формуле и Вижинер по таблице дают одинаковый результат")
    void trithemiusEqualsVigenere() {
        String text = "ГРУЗИТЕ АПЕЛЬСИНЫ БОЧКАМИ";

        assertEquals(Algorithm.trithemius(text, "ВЕНТИЛЬ", false), Algorithm.vigenere(text, "ВЕНТИЛЬ", false));
    }

    @Test
    @Order(13)
    @DisplayName("Ошибка: пустой ключ")
    void emptyKeyIsError() {
        assertThrows(IllegalArgumentException.class, () -> Algorithm.trithemius("ПРИВЕТ", "", false));
        assertThrows(IllegalArgumentException.class, () -> Algorithm.vigenere("ПРИВЕТ", "   ", false));
    }

    @Test
    @Order(14)
    @DisplayName("Ошибка: ключ с посторонними символами")
    void keyWithExtraSymbolsIsError() {
        assertThrows(IllegalArgumentException.class, () -> Algorithm.trithemius("ПРИВЕТ", "КЛЮЧ1", false));
        assertThrows(IllegalArgumentException.class, () -> Algorithm.vigenere("ПРИВЕТ", "KEY", false));
    }

    @Test
    @Order(15)
    @DisplayName("Ошибка: нечисловой или пустой сдвиг")
    void notNumberShiftIsError() {
        assertThrows(IllegalArgumentException.class, () -> Util.parseShift("три"));
        assertThrows(IllegalArgumentException.class, () -> Util.parseShift(""));
    }

    @Test
    @Order(16)
    @DisplayName("Таблица Вижинера имеет размер 32×32 и построена циклическим сдвигом")
    void vigenereTableSize() {
        char[][] table = Util.vigenereTable();

        assertEquals(32, table.length);
        assertEquals(32, table[0].length);
        assertEquals('Я', table[31][0]);
        assertEquals('Ю', table[31][31]);
    }
}
