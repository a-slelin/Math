package a.slelin.work.math.security.analytic;

import lombok.experimental.UtilityClass;

/**
 * Матричный шифр: умеет только зашифровать текст и расшифровать числа.
 * Вся линейная алгебра — в классе {@link LinAlg}, работа с алфавитом — в классе {@link Util}.
 */
@UtilityClass
public class Decoder {

    /**
     * Шифрование C = A × B по п. 2.2:
     * 1) буквы текста заменяются номерами в алфавите;
     * 2) текст дополняется буквой Ъ до длины, кратной порядку ключа n;
     * 3) номера разбиваются на векторы B₁, B₂, … по n чисел;
     * 4) каждый вектор умножается на матрицу-ключ: Cₖ = A × Bₖ;
     * 5) компоненты всех Cₖ выписываются подряд (по модулю НЕ приводятся).
     *
     * @param text исходный текст (регистр не важен, пробелы и знаки отбрасываются)
     * @param key  квадратная невырожденная целочисленная матрица-ключ
     * @return шифротекст — последовательность чисел
     */
    public long[] encrypt(String text, long[][] key) {
        checkKey(key);

        String clean = Util.normalize(text);
        if (clean.isEmpty()) {
            throw new IllegalArgumentException("Текст не содержит ни одной русской буквы.");
        }

        int n = key.length;
        long[] numbers = Util.toNumbers(Util.pad(clean, n));
        long[] result = new long[numbers.length];

        // Каждый блок B умножаем на ключ и записываем результат C на то же место;
        int position = 0;
        for (long[] block : Util.blocks(numbers, n)) {
            for (long c : LinAlg.multiply(key, block)) {
                result[position++] = c;
            }
        }

        return result;
    }

    /**
     * Расшифровка B = A⁻¹ × C по п. 2.3: обратная матрица A⁻¹ = (1/Δ) · (A*)ᵀ
     * умножается на каждый блок шифротекста, компоненты результата — номера букв.
     * Дополняющие буквы Ъ в конце НЕ отбрасываются (см. {@link Util#unpad(String)}).
     *
     * @param numbers шифротекст — последовательность чисел, длина кратна порядку ключа
     * @param key     та же матрица-ключ, которой выполнялось шифрование
     * @return открытый текст заглавными буквами
     */
    public String decrypt(long[] numbers, long[][] key) {
        checkKey(key);

        int n = key.length;
        if (numbers.length == 0 || numbers.length % n != 0) {
            throw new IllegalArgumentException("Неверный ключ или шифротекст: количество чисел ("
                    + numbers.length + ") не кратно порядку ключа n = " + n + ".");
        }

        LinAlg.Fraction[][] inverse = LinAlg.inverse(key);
        StringBuilder result = new StringBuilder();

        for (long[] block : Util.blocks(numbers, n)) {
            for (LinAlg.Fraction b : LinAlg.multiply(inverse, block)) {
                // При правильных ключе и шифротексте получаются целые числа от 0 до 32;
                if (!b.isInteger() || b.num() < 0 || b.num() >= Util.N) {
                    throw new IllegalArgumentException("Неверный ключ или шифротекст: в блоке "
                            + Util.vector(block) + " получено число " + b + ", а не номер буквы 0…"
                            + (Util.N - 1) + ".");
                }
                result.append(Util.letterAt(b.num()));
            }
        }

        return result.toString();
    }

    /**
     * Проверка ключа: матрица квадратная и невырожденная (Δ ≠ 0), иначе расшифровка невозможна.
     */
    public void checkKey(long[][] key) {
        Util.checkSquare(key);

        if (LinAlg.det(key) == 0) {
            throw new IllegalArgumentException("Матрица-ключ вырождена: det = 0, расшифровка невозможна.");
        }
    }
}
