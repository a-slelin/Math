public class Main {
    public static int N = 1000000000;
    public static double start = 2/7.0;
    public static int afterComma = 10;
    public static String format = "%." + afterComma + "f";

    public static void main(String[] args){
        double x_n, y_n, z_n, w_n;
        x_n = y_n = z_n = w_n = start;
        double max_xy, max_zw;
        max_zw = max_xy = 0;


        for (int i = 0; i < N; ++i){
            z_n = 3 * z_n * (1 - z_n);
            w_n = 3 * w_n - 3 * w_n * w_n;
            max_zw = Math.max(max_zw, Math.abs(z_n - w_n));

            x_n = 4 * x_n * (1 - x_n);
            y_n = 4 * y_n - 4 * y_n * y_n;
            max_xy = Math.max(max_xy, Math.abs(x_n - y_n));
        }
        System.out.println("We do not have a chaos:");
        System.out.println("z_n = " + String.format(format, z_n));
        System.out.println("w_n = " + String.format(format, w_n));
        System.out.println("|z_n - w_n| = " + String.format(format, Math.abs(z_n - w_n)));
        System.out.println("max |z_k - w_k| = " + String.format(format, max_zw));

        System.out.println();
        System.out.println("We have a chaos:");
        System.out.println("x_n = " + String.format(format, x_n));
        System.out.println("y_n = " + String.format(format, y_n));
        System.out.println("|x_n - y_n| = " + String.format(format, Math.abs(x_n - y_n)));
        System.out.println("max |x_k - y_k| = " + String.format(format, max_xy));
    }
}
