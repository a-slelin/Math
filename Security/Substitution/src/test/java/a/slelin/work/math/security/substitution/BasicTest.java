package a.slelin.work.math.security.substitution;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

/**
 * Тестовые данные для самопроверки из пункта 4.4 методички,
 * а также проверка обязательных требований из пункта 4.1.
 */
public class BasicTest {

    // ===================== Пункт 4.4 =====================

    @Test
    void caesarEncryptAlphabet() {
        assertEquals("ГОЧГЕЛХ", Algorithm.caesar("АЛФАВИТ", 3, false));
    }

    @Test
    void caesarEncryptApple() {
        assertEquals("АВМПЛП", Algorithm.caesar("ЯБЛОКО", 1, false));
    }

    @Test
    void caesarEncryptEndOfAlphabet() {
        // После «Я» снова идёт «А» (алфавит замкнут в кольцо);
        assertEquals("АБВ", Algorithm.caesar("ЭЮЯ", 3, false));
    }

    @Test
    void caesarDecryptAlphabet() {
        assertEquals("АЛФАВИТ", Algorithm.caesar("ГОЧГЕЛХ", 3, true));
    }

    @Test
    void trithemiusEncryptHello() {
        assertEquals("ЦРЧКЦМ", Algorithm.trithemius("ПРИВЕТ", "ЗАПИСЬ", false));
    }

    @Test
    void vigenereEncryptLoad() {
        assertEquals("ЕХАЩРЭЯ", Algorithm.vigenere("ГРУЗИТЕ", "ВЕНТИЛЬ", false));
    }

    @Test
    void vigenereDecryptLoad() {
        assertEquals("ГРУЗИТЕ", Algorithm.vigenere("ЕХАЩРЭЯ", "ВЕНТИЛЬ", true));
    }

    // ===================== Примеры из теории =====================

    @Test
    void trithemiusExampleFromTheory() {
        String text = "В связи с создавшимся положением отодвигаем сроки возвращения домой Рамзай";
        String expected = "ЙССЗШ ВШСЭП ХЬЙШЧ ФВЩЦО ЬЦЧЯФ ИФФЯМ ХДСРФ ЬММАШ ЯДПВЭ ПУКЗЩ ФХЩЩЛ ОЫЦЬК ЗМЦИЬ";

        assertEquals(expected, Util.groupByFive(Algorithm.trithemius(text, "ЗАПИСЬ", false)));
    }

    @Test
    void vigenereExampleFromTheory() {
        String expected = "ЕХАЩР ЭЯВФТ ЭВЪВП АОАЯХ ЬОН";

        assertEquals(expected, Util.groupByFive(Algorithm.vigenere("ГРУЗИТЕ АПЕЛЬСИНЫ БОЧКАМИ", "ВЕНТИЛЬ", false)));
    }

    // ===================== Требования пункта 4.1 =====================

    @Test
    void normalizeRemovesExtraSymbols() {
        // Регистр не учитывается, «ё» → «е», пробелы, цифры и знаки препинания удаляются;
        assertEquals("ЕЛКАЕЖИК", Util.normalize("Ёлка, ёжик! 123"));
    }

    @Test
    void caesarNegativeAndBigShift() {
        // Сдвиг 35 = 3 (mod 32), сдвиг -29 = 3 (mod 32);
        assertEquals("ГОЧГЕЛХ", Algorithm.caesar("АЛФАВИТ", 35, false));
        assertEquals("ГОЧГЕЛХ", Algorithm.caesar("АЛФАВИТ", -29, false));
    }

    @Test
    void trithemiusEqualsVigenere() {
        // Арифметический шифр Тритемиуса и табличный шифр Вижинера дают одинаковый результат;
        String text = "ГРУЗИТЕ АПЕЛЬСИНЫ БОЧКАМИ";

        assertEquals(Algorithm.trithemius(text, "ВЕНТИЛЬ", false), Algorithm.vigenere(text, "ВЕНТИЛЬ", false));
    }

    @Test
    void emptyKeyIsError() {
        assertThrows(IllegalArgumentException.class, () -> Algorithm.trithemius("ПРИВЕТ", "", false));
        assertThrows(IllegalArgumentException.class, () -> Algorithm.vigenere("ПРИВЕТ", "   ", false));
    }

    @Test
    void keyWithExtraSymbolsIsError() {
        assertThrows(IllegalArgumentException.class, () -> Algorithm.trithemius("ПРИВЕТ", "КЛЮЧ1", false));
        assertThrows(IllegalArgumentException.class, () -> Algorithm.vigenere("ПРИВЕТ", "KEY", false));
    }

    @Test
    void notNumberShiftIsError() {
        assertThrows(IllegalArgumentException.class, () -> Util.parseShift("три"));
        assertThrows(IllegalArgumentException.class, () -> Util.parseShift(""));
    }

    @Test
    void vigenereTableSize() {
        char[][] table = Util.vigenereTable();

        assertEquals(32, table.length);
        assertEquals(32, table[0].length);
        assertEquals('Я', table[31][0]);
        assertEquals('Ю', table[31][31]);
    }
}
