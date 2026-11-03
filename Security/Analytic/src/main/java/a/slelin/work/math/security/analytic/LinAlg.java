package a.slelin.work.math.security.analytic;

import lombok.experimental.UtilityClass;

import java.util.Random;

/**
 * Линейная алгебра для матричного шифрования, реализованная самостоятельно (без сторонних библиотек):
 * определитель, миноры, алгебраические дополнения, транспонирование, обратная матрица,
 * умножение матриц и векторов, а также генерация ключей с определителем ±1 (дополнительное задание).
 * <p>
 * Все вычисления точные: целые числа ({@code long} с контролем переполнения)
 * и рациональные дроби {@link Fraction} — никакого округления.
 */
@UtilityClass
public class LinAlg {

    /**
     * Точная рациональная дробь num / den.
     * Дробь всегда хранится в несократимом виде, знаменатель положителен (например, 6/-8 → -3/4).
     */
    public record Fraction(long num, long den) {

        /**
         * Канонический конструктор: проверка знаменателя и сокращение дроби.
         */
        public Fraction {
            if (den == 0) {
                throw new ArithmeticException("Знаменатель дроби равен нулю.");
            }

            // Знак переносим в числитель;
            if (den < 0) {
                num = Math.negateExact(num);
                den = Math.negateExact(den);
            }

            // Сокращаем на наибольший общий делитель;
            long gcd = gcd(Math.abs(num), den);
            num /= gcd;
            den /= gcd;
        }

        /**
         * Целое число как дробь: 5 → 5/1.
         */
        public static Fraction of(long value) {
            return new Fraction(value, 1);
        }

        /**
         * Сумма дробей: a/b + c/d = (ad + cb) / bd.
         */
        public Fraction plus(Fraction other) {
            return new Fraction(
                    Math.addExact(Math.multiplyExact(num, other.den), Math.multiplyExact(other.num, den)),
                    Math.multiplyExact(den, other.den));
        }

        /**
         * Произведение дробей: a/b · c/d = ac / bd.
         */
        public Fraction times(Fraction other) {
            return new Fraction(Math.multiplyExact(num, other.num), Math.multiplyExact(den, other.den));
        }

        /**
         * Является ли дробь целым числом (знаменатель равен 1).
         */
        public boolean isInteger() {
            return den == 1;
        }

        /**
         * Запись дроби: целое число без знаменателя (3), иначе через черту (-3/8).
         */
        @Override
        public String toString() {
            return isInteger() ? String.valueOf(num) : num + "/" + den;
        }

        /**
         * Наибольший общий делитель (алгоритм Евклида). НОД(0, b) = b, поэтому 0/5 → 0/1.
         */
        private static long gcd(long a, long b) {
            while (b != 0) {
                long rest = a % b;
                a = b;
                b = rest;
            }

            return a;
        }
    }

    // ===================== Определитель и миноры =====================

    /**
     * Определитель квадратной матрицы разложением по первой строке (формула Лапласа):
     * Δ = Σ a₁ⱼ · A₁ⱼ = Σ (−1)^(1+j) · a₁ⱼ · M₁ⱼ.
     * Для матрицы 1×1 определитель равен её единственному элементу, для пустой (0×0) — единице.
     */
    public long det(long[][] m) {
        int n = m.length;

        if (n == 0) {
            return 1;
        }
        if (n == 1) {
            return m[0][0];
        }

        long result = 0;
        for (int j = 0; j < n; j++) {
            long term = Math.multiplyExact(m[0][j], minor(m, 0, j));
            result = (j % 2 == 0) ? Math.addExact(result, term) : Math.subtractExact(result, term);
        }

        return result;
    }

    /**
     * Минор Mᵢⱼ — определитель матрицы, полученной вычёркиванием i-й строки и j-го столбца.
     * Индексы считаются с нуля.
     */
    public long minor(long[][] m, int i, int j) {
        return det(submatrix(m, i, j));
    }

    /**
     * Матрица без i-й строки и j-го столбца.
     */
    public long[][] submatrix(long[][] m, int i, int j) {
        int n = m.length;
        long[][] result = new long[n - 1][n - 1];

        for (int row = 0, r = 0; row < n; row++) {
            if (row == i) {
                continue;
            }

            for (int column = 0, c = 0; column < n; column++) {
                if (column == j) {
                    continue;
                }
                result[r][c++] = m[row][column];
            }
            r++;
        }

        return result;
    }

    /**
     * Матрица алгебраических дополнений A*: Aᵢⱼ = (−1)^(i+j) · Mᵢⱼ.
     */
    public long[][] cofactors(long[][] m) {
        int n = m.length;
        long[][] result = new long[n][n];

        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                long minor = minor(m, i, j);
                result[i][j] = ((i + j) % 2 == 0) ? minor : Math.negateExact(minor);
            }
        }

        return result;
    }

    /**
     * Транспонирование: строки становятся столбцами.
     */
    public long[][] transpose(long[][] m) {
        int rows = m.length;
        int columns = rows == 0 ? 0 : m[0].length;
        long[][] result = new long[columns][rows];

        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < columns; j++) {
                result[j][i] = m[i][j];
            }
        }

        return result;
    }

    /**
     * Обратная матрица по схеме из п. 2.3: A⁻¹ = (1/Δ) · (A*)ᵀ.
     * Если определитель равен нулю, матрица вырождена и обратной у неё нет.
     */
    public Fraction[][] inverse(long[][] m) {
        long det = det(m);
        if (det == 0) {
            throw new IllegalArgumentException("Матрица вырождена (det = 0), обратной матрицы не существует.");
        }

        long[][] adjugate = transpose(cofactors(m));
        int n = m.length;
        Fraction[][] result = new Fraction[n][n];

        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                result[i][j] = new Fraction(adjugate[i][j], det);
            }
        }

        return result;
    }

    // ===================== Умножение =====================

    /**
     * Умножение целочисленной матрицы на вектор: cᵢ = Σ aᵢⱼ · bⱼ.
     */
    public long[] multiply(long[][] m, long[] vector) {
        long[] result = new long[m.length];

        for (int i = 0; i < m.length; i++) {
            for (int j = 0; j < vector.length; j++) {
                result[i] = Math.addExact(result[i], Math.multiplyExact(m[i][j], vector[j]));
            }
        }

        return result;
    }

    /**
     * Умножение матрицы дробей на целочисленный вектор (используется при расшифровке).
     */
    public Fraction[] multiply(Fraction[][] m, long[] vector) {
        Fraction[] result = new Fraction[m.length];

        for (int i = 0; i < m.length; i++) {
            result[i] = Fraction.of(0);
            for (int j = 0; j < vector.length; j++) {
                result[i] = result[i].plus(m[i][j].times(Fraction.of(vector[j])));
            }
        }

        return result;
    }

    /**
     * Произведение целочисленной матрицы на матрицу дробей (для проверки A · A⁻¹ = E).
     */
    public Fraction[][] multiply(long[][] a, Fraction[][] b) {
        int n = a.length;
        Fraction[][] result = new Fraction[n][b[0].length];

        for (int i = 0; i < n; i++) {
            for (int j = 0; j < b[0].length; j++) {
                result[i][j] = Fraction.of(0);
                for (int k = 0; k < b.length; k++) {
                    result[i][j] = result[i][j].plus(Fraction.of(a[i][k]).times(b[k][j]));
                }
            }
        }

        return result;
    }

    /**
     * Является ли матрица дробей единичной (E: единицы на диагонали, нули вне её).
     */
    public boolean isIdentity(Fraction[][] m) {
        for (int i = 0; i < m.length; i++) {
            for (int j = 0; j < m[i].length; j++) {
                if (!m[i][j].equals(Fraction.of(i == j ? 1 : 0))) {
                    return false;
                }
            }
        }

        return true;
    }

    /**
     * Перевод матрицы дробей в целочисленную. Удаётся, только если все элементы — целые числа
     * (например, обратная матрица ключа с определителем ±1).
     */
    public long[][] toLong(Fraction[][] m) {
        long[][] result = new long[m.length][];

        for (int i = 0; i < m.length; i++) {
            result[i] = new long[m[i].length];
            for (int j = 0; j < m[i].length; j++) {
                if (!m[i][j].isInteger()) {
                    throw new IllegalArgumentException("Элемент " + m[i][j] + " не является целым числом.");
                }
                result[i][j] = m[i][j].num();
            }
        }

        return result;
    }

    // ===================== Генерация ключей (дополнительное задание) =====================

    /**
     * Случайная целочисленная матрица порядка n с определителем ±1 (унимодулярная матрица).
     * <p>
     * Идея: матрица L с единицами на диагонали и случайными числами ниже неё имеет det L = 1,
     * то же верно для матрицы U с числами выше диагонали. Значит, det(L · U) = 1 · 1 = 1.
     * Затем случайно переставляем строки (каждая перестановка двух строк меняет знак определителя)
     * — получаем det = ±1. Поэтому обратная матрица (1/Δ) · (A*)ᵀ тоже целочисленная.
     *
     * @param n      порядок матрицы (2, 3, 4, …)
     * @param random генератор случайных чисел (можно передать с фиксированным seed для тестов)
     */
    public long[][] randomUnimodular(int n, Random random) {
        if (n < 1) {
            throw new IllegalArgumentException("Порядок матрицы должен быть положительным.");
        }

        long[][] lower = identity(n);
        long[][] upper = identity(n);

        // Небольшие числа от -2 до 2, чтобы шифротекст был обозримым;
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < i; j++) {
                lower[i][j] = random.nextInt(5) - 2;
                upper[j][i] = random.nextInt(5) - 2;
            }
        }

        long[][] result = multiply(lower, upper);

        // Случайная перестановка строк (тасование Фишера — Йетса);
        for (int i = n - 1; i > 0; i--) {
            int k = random.nextInt(i + 1);
            long[] row = result[i];
            result[i] = result[k];
            result[k] = row;
        }

        return result;
    }

    /**
     * Единичная матрица порядка n.
     */
    public long[][] identity(int n) {
        long[][] result = new long[n][n];

        for (int i = 0; i < n; i++) {
            result[i][i] = 1;
        }

        return result;
    }

    /**
     * Произведение двух целочисленных матриц.
     */
    public long[][] multiply(long[][] a, long[][] b) {
        long[][] result = new long[a.length][];

        // Элемент (i, j) — скалярное произведение i-й строки a на j-й столбец b;
        for (int i = 0; i < a.length; i++) {
            result[i] = new long[b[0].length];
            for (int j = 0; j < b[0].length; j++) {
                for (int k = 0; k < b.length; k++) {
                    result[i][j] = Math.addExact(result[i][j], Math.multiplyExact(a[i][k], b[k][j]));
                }
            }
        }

        return result;
    }
}
