package a.slelin.work.math.security.analytic;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.MethodOrderer;
import org.junit.jupiter.api.Order;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestMethodOrder;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

import java.util.Random;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

@DisplayName("Проверка ручного решения (часть А), вариант 2")
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
public class CheckTests {

    /**
     * Матрица-ключ из заданий 1 и 2 (det = 8).
     */
    static final long[][] A = {{3, 2, 1}, {2, 5, 3}, {3, 4, 3}};

    /**
     * Матрица-ключ из задания 3 (det = 1).
     */
    static final long[][] A3 = {{14, 8, 3}, {8, 5, 2}, {3, 2, 1}};

    /**
     * Матрица из задания 4 (det = 6).
     */
    static final long[][] D = {{2, 1, 1}, {1, 3, 2}, {1, 1, 2}};

    /**
     * Матрица-ключ из задания 5 (det = 3).
     */
    static final long[][] K = {{2, 1}, {1, 2}};

    @Test
    @Order(1)
    @DisplayName("Задание 1А. КОРОЛЬ → 80 148 144 96 171 174 → КОРОЛЬ")
    void task1aKing() {
        long[] cipher = Decoder.encrypt("КОРОЛЬ", A);

        assertArrayEquals(new long[]{80, 148, 144, 96, 171, 174}, cipher);
        assertEquals("КОРОЛЬ", Decoder.decrypt(cipher, A));
    }

    @Test
    @Order(2)
    @DisplayName("Задание 1Б. ТУРНИР → 114 189 188 77 124 129 → ТУРНИР")
    void task1bTournament() {
        long[] cipher = Decoder.encrypt("ТУРНИР", A);

        assertArrayEquals(new long[]{114, 189, 188, 77, 124, 129}, cipher);
        assertEquals("ТУРНИР", Decoder.decrypt(cipher, A));
    }

    @Test
    @Order(3)
    @DisplayName("Задание 2. 67 68 87 88 151 150 90 189 180 → ТАЙНОПИСЬ")
    void task2Decrypt() {
        assertEquals("ТАЙНОПИСЬ", Decoder.decrypt(new long[]{67, 68, 87, 88, 151, 150, 90, 189, 180}, A));
    }

    @Test
    @Order(4)
    @DisplayName("Задание 3. Обратная матрица ключа с det = 1 целочисленная")
    void task3Inverse() {
        assertEquals(1, LinAlg.det(A3));
        assertArrayEquals(new long[][]{{1, -2, 1}, {-2, 5, -4}, {1, -4, 6}}, LinAlg.toLong(LinAlg.inverse(A3)));
    }

    @Test
    @Order(5)
    @DisplayName("Задание 3. Шифрование: ТАЙНИК → 296 172 67 301 179 71")
    void task3EncryptCache() {
        assertArrayEquals(new long[]{296, 172, 67, 301, 179, 71}, Decoder.encrypt("ТАЙНИК", A3));
    }

    @Test
    @Order(6)
    @DisplayName("Задание 3. Шифрование: МАСТЕР → 236 140 57 357 211 84")
    void task3EncryptMaster() {
        assertArrayEquals(new long[]{236, 140, 57, 357, 211, 84}, Decoder.encrypt("МАСТЕР", A3));
    }

    @Test
    @Order(7)
    @DisplayName("Задание 3А. Расшифровка: 196 123 52 412 247 99 → ВОПРОС")
    void task3aDecrypt() {
        assertEquals("ВОПРОС", Decoder.decrypt(new long[]{196, 123, 52, 412, 247, 99}, A3));
    }

    @Test
    @Order(8)
    @DisplayName("Задание 3Б. Расшифровка: 292 178 73 … 116 71 28 → ИНСЦЕНИРОВКА")
    void task3bDecrypt() {
        long[] cipher = {292, 178, 73, 404, 237, 93, 307, 187, 76, 116, 71, 28};

        assertEquals("ИНСЦЕНИРОВКА", Decoder.decrypt(cipher, A3));
    }

    @Test
    @Order(9)
    @DisplayName("Задание 4. det D = 6, алгебраические дополнения и D · D⁻¹ = E")
    void task4Inverse() {
        LinAlg.Fraction[][] inverse = LinAlg.inverse(D);

        assertEquals(6, LinAlg.det(D));
        assertArrayEquals(new long[][]{{4, 0, -2}, {-1, 3, -1}, {-1, -3, 5}}, LinAlg.cofactors(D));
        assertArrayEquals(new LinAlg.Fraction[][]{
                {new LinAlg.Fraction(2, 3), new LinAlg.Fraction(-1, 6), new LinAlg.Fraction(-1, 6)},
                {new LinAlg.Fraction(0, 1), new LinAlg.Fraction(1, 2), new LinAlg.Fraction(-1, 2)},
                {new LinAlg.Fraction(-1, 3), new LinAlg.Fraction(-1, 6), new LinAlg.Fraction(5, 6)}
        }, inverse);
        assertTrue(LinAlg.isIdentity(LinAlg.multiply(D, inverse)));
    }

    @Test
    @Order(10)
    @DisplayName("Задание 5А. МАТРИЦА (+Ъ) → 26 13 55 53 41 55 29 58")
    void task5aEncrypt() {
        long[] cipher = Decoder.encrypt("МАТРИЦА", K);

        assertArrayEquals(new long[]{26, 13, 55, 53, 41, 55, 29, 58}, cipher);
        assertEquals("МАТРИЦА", Util.unpad(Decoder.decrypt(cipher, K)));
    }

    @Test
    @Order(11)
    @DisplayName("Задание 5Б. Расшифровка: 59 43 59 55 → ШИФР")
    void task5bDecrypt() {
        assertEquals("ШИФР", Decoder.decrypt(new long[]{59, 43, 59, 55}, K));
    }

    @ParameterizedTest(name = "n = {0}")
    @Order(12)
    @ValueSource(ints = {2, 3, 4})
    @DisplayName("Доп. задание. Генератор ключей: det = ±1, обратная целочисленная, ВАРИАНТ → … → ВАРИАНТ")
    void extraKeyGenerator(int n) {
        Random random = new Random(2);

        // Проверяем несколько случайных ключей каждого порядка;
        for (int attempt = 0; attempt < 100; attempt++) {
            long[][] key = LinAlg.randomUnimodular(n, random);

            assertEquals(1, Math.abs(LinAlg.det(key)));
            LinAlg.toLong(LinAlg.inverse(key));
            assertEquals("ВАРИАНТ", Util.unpad(Decoder.decrypt(Decoder.encrypt("ВАРИАНТ", key), key)));
        }
    }
}
