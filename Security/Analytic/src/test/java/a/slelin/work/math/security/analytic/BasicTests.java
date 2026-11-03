package a.slelin.work.math.security.analytic;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.MethodOrderer;
import org.junit.jupiter.api.Order;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestMethodOrder;

import java.util.List;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

@DisplayName("Базовые тесты")
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
public class BasicTests {

    /**
     * Ключ из примера п. 2.2 (det = 8).
     */
    static final long[][] A = {{3, 2, 1}, {2, 5, 3}, {3, 4, 3}};

    /**
     * Ключ третьего порядка с det = 1.
     */
    static final long[][] B = {{14, 8, 3}, {8, 5, 2}, {3, 2, 1}};

    /**
     * Ключ второго порядка с det = 1.
     */
    static final long[][] K = {{2, 1}, {5, 3}};

    // Тестовые данные для самопроверки из пункта 4.4

    @Test
    @Order(1)
    @DisplayName("4.4. Шифрование: ЗАБАВА ключом [[3,2,1],[2,5,3],[3,4,3]] → 25 19 27 4 10 8")
    void encryptZabava() {
        assertArrayEquals(new long[]{25, 19, 27, 4, 10, 8}, Decoder.encrypt("ЗАБАВА", A));
    }

    @Test
    @Order(2)
    @DisplayName("4.4. Расшифровка: 25 19 27 4 10 8 ключом [[3,2,1],[2,5,3],[3,4,3]] → ЗАБАВА")
    void decryptZabava() {
        assertEquals("ЗАБАВА", Decoder.decrypt(new long[]{25, 19, 27, 4, 10, 8}, A));
    }

    @Test
    @Order(3)
    @DisplayName("4.4. Расшифровка: 108 197 198 74 157 156 ключом [[3,2,1],[2,5,3],[3,4,3]] → ПОЭЗИЯ")
    void decryptPoetry() {
        assertEquals("ПОЭЗИЯ", Decoder.decrypt(new long[]{108, 197, 198, 74, 157, 156}, A));
    }

    @Test
    @Order(4)
    @DisplayName("4.4. Расшифровка: 357 217 89 224 132 53 ключом [[14,8,3],[8,5,2],[3,2,1]] → ЛОЦМАН")
    void decryptPilot() {
        assertEquals("ЛОЦМАН", Decoder.decrypt(new long[]{357, 217, 89, 224, 132, 53}, B));
    }

    @Test
    @Order(5)
    @DisplayName("4.4. Шифрование: ШИФР ключом [[2,1],[5,3]] → 59 152 59 156")
    void encryptCipher() {
        assertArrayEquals(new long[]{59, 152, 59, 156}, Decoder.encrypt("ШИФР", K));
    }

    @Test
    @Order(6)
    @DisplayName("4.4. Шифрование: КОД (с «Ъ») ключом [[2,1],[5,3]] → 37 100 37 107")
    void encryptCodeWithPadding() {
        assertArrayEquals(new long[]{37, 100, 37, 107}, Decoder.encrypt("КОД", K));
    }

    @Test
    @Order(7)
    @DisplayName("4.4. Шифрование: ТЕКСТ ключом [[1,2],[2,4]] → ошибка: det = 0")
    void degenerateKeyIsError() {
        IllegalArgumentException e = assertThrows(IllegalArgumentException.class,
                () -> Decoder.encrypt("ТЕКСТ", new long[][]{{1, 2}, {2, 4}}));

        assertTrue(e.getMessage().contains("det = 0"));
    }

    // Тесты на проверку требований пункта 4.1

    @Test
    @Order(8)
    @DisplayName("Алфавит из 33 букв: А = 0, Ё = 6, Ь = 27, Ы = 28, Ъ = 29, Я = 32")
    void alphabetOrder() {
        assertEquals(33, Util.N);
        assertArrayEquals(new long[]{0, 6, 27, 28, 29, 32}, Util.toNumbers("АЁЬЫЪЯ"));
    }

    @Test
    @Order(9)
    @DisplayName("Подготовка текста: регистр не учитывается, пробелы, цифры и знаки удаляются")
    void normalizeRemovesExtraSymbols() {
        assertEquals("ЗАБАВА", Util.normalize("за-Ба, ва! 123"));
        assertArrayEquals(Decoder.encrypt("ЗАБАВА", A), Decoder.encrypt("за ба ва", A));
    }

    @Test
    @Order(10)
    @DisplayName("Разбор ключа: матрица должна быть квадратной и целочисленной")
    void parseMatrixChecks() {
        assertArrayEquals(K, Util.parseMatrix(List.of("2 1", "5 3")));
        assertThrows(IllegalArgumentException.class, () -> Util.parseMatrix(List.of("2 1 0", "5 3")));
        assertThrows(IllegalArgumentException.class, () -> Util.parseMatrix(List.of("2 1.5", "5 3")));
        assertThrows(IllegalArgumentException.class, () -> Decoder.encrypt("ТЕКСТ", new long[][]{{1, 2}}));
    }

    @Test
    @Order(11)
    @DisplayName("Определитель, миноры и алгебраические дополнения ключа из примера п. 2.3")
    void detAndCofactors() {
        assertEquals(8, LinAlg.det(A));
        assertEquals(3, LinAlg.minor(A, 0, 0));
        assertArrayEquals(new long[][]{{3, 3, -7}, {-2, 6, -6}, {1, -7, 11}}, LinAlg.cofactors(A));
        assertArrayEquals(new long[][]{{3, -2, 1}, {3, 6, -7}, {-7, -6, 11}}, LinAlg.transpose(LinAlg.cofactors(A)));
    }

    @Test
    @Order(12)
    @DisplayName("Точная обратная матрица из дробей: A · A⁻¹ = E")
    void inverseIsExact() {
        LinAlg.Fraction[][] inverse = LinAlg.inverse(A);

        assertEquals(new LinAlg.Fraction(3, 8), inverse[0][0]);
        assertEquals(new LinAlg.Fraction(-1, 4), inverse[0][1]);
        assertTrue(LinAlg.isIdentity(LinAlg.multiply(A, inverse)));
    }

    @Test
    @Order(13)
    @DisplayName("Ключ четвёртого порядка: det и шифрование туда-обратно")
    void fourthOrderKey() {
        long[][] key = {{1, 2, 0, 1}, {0, 1, 3, 0}, {1, 0, 1, 2}, {0, 1, 0, 1}};

        long[] cipher = Decoder.encrypt("ВЫЧИСЛЕНИЕ", key);

        assertEquals(10, LinAlg.det(key));
        assertEquals(12, cipher.length);
        assertEquals("ВЫЧИСЛЕНИЕЪЪ", Decoder.decrypt(cipher, key));
    }

    @Test
    @Order(14)
    @DisplayName("Ошибка: длина шифротекста не кратна порядку ключа")
    void wrongCipherLengthIsError() {
        IllegalArgumentException e = assertThrows(IllegalArgumentException.class,
                () -> Decoder.decrypt(new long[]{25, 19, 27, 4}, A));

        assertTrue(e.getMessage().contains("Неверный ключ или шифротекст"));
    }

    @Test
    @Order(15)
    @DisplayName("Ошибка: результат расшифровки не целый или вне диапазона 0…32")
    void wrongCipherIsError() {
        // Дробный результат (25 заменено на 26);
        assertThrows(IllegalArgumentException.class, () -> Decoder.decrypt(new long[]{26, 19, 27, 4, 10, 8}, A));

        // Целый, но отрицательный результат (ключ с det = 1);
        assertThrows(IllegalArgumentException.class, () -> Decoder.decrypt(new long[]{0, 0, 1}, B));
    }

    @Test
    @Order(16)
    @DisplayName("Дополнение буквой Ъ при шифровании и его отбрасывание после расшифровки")
    void paddingAndUnpadding() {
        String text = Decoder.decrypt(Decoder.encrypt("КОД", K), K);

        assertEquals("КОДЪ", text);
        assertEquals("КОД", Util.unpad(text));
    }
}
