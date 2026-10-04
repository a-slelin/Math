import numpy as np
from const import n, eps, exact
from draw import plot_solutions, plot_errors, plot_convergence
from methods import check_contraction, successive_approximations, linear_system


# Главная функция: решаем уравнение тремя способами и сравниваем результаты
def main():
    print('Уравнение Фредгольма второго рода (вариант 3):')
    print('  φ(t) = ∫[0, π/5] (5/π)·sin(5t+5s)·φ(s) ds + 1.5·sin(5t)\n')

    # Шаг 1. Проверяем условия сжимаемости оператора A при λ = 1
    M, B, c_value, l2_value = check_contraction()
    print('Проверка сжимаемости оператора A (λ = 1):')
    print(f'  M = max|K| = {M:.6f},  |λ|·M·(b−a) = {c_value:.6f}  ->  '
          f'{"выполнено" if c_value < 1 else "НЕ выполнено"} (нужно < 1)')
    print(f'  B = ||K||_L2 = {B:.6f},  |λ|·B = {l2_value:.6f}  ->  '
          f'{"выполнено" if l2_value < 1 else "НЕ выполнено"} (нужно < 1)\n')

    # Шаг 2. Метод последовательных приближений
    grid, phi_iter, differences = successive_approximations()
    print(f'Метод последовательных приближений: {len(differences)} шагов до точности {eps}')

    # Шаг 3. Метод сведения к СЛАУ
    _, phi_slae = linear_system()
    print(f'Метод СЛАУ: решена система из {n + 1} уравнений')

    # Шаг 4. Сравниваем с точным решением φ(t) = 2·sin(5t) + cos(5t)
    error_iter = np.max(np.abs(phi_iter - exact(grid)))
    error_slae = np.max(np.abs(phi_slae - exact(grid)))
    print('\nМаксимальная ошибка по сравнению с точным решением:')
    print(f'  последовательные приближения: {error_iter:.3e}')
    print(f'  СЛАУ:                         {error_slae:.3e}')
    print(f'  разница между двумя методами: {np.max(np.abs(phi_iter - phi_slae)):.3e}')

    # Шаг 5. Рисуем графики
    plot_solutions(grid, phi_iter, phi_slae)
    plot_errors(grid, phi_iter, phi_slae)
    plot_convergence(differences)


if __name__ == '__main__':
    main()
