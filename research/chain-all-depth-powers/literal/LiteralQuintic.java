/*
 * Literal depth-five census. SHIN09-git with OpenAI Codex assistance.
 * Apache-2.0. Run with a JDK supporting single-file source launch.
 */
import java.util.Arrays;

class LiteralQuintic {
    private static final int LABELS = 5;

    private static long factorial(int value) {
        long result = 1;
        for (int k = 2; k <= value; k++) result *= k;
        return result;
    }

    private static int endpoint(int[][] action, int modulus) {
        // Singletons equal modulus by construction. Retain all nine other
        // proper intervals, then read the bottom-left target coefficient.
        for (int end = 2; end <= LABELS; end++) {
            for (int column = 0; column < end - 1; column++) {
                if (end == LABELS && column == 0) continue;
                if (action[end][column] % modulus != 0) return -1;
            }
        }
        return action[LABELS][0] % modulus;
    }

    private static void shear(int[][] action, int label, int sign) {
        for (int column = 0; column < label; column++) {
            action[label][column] += sign * action[label-1][column];
        }
    }

    private static String enumerate(int n) {
        if (n != 2 && n != 3) throw new IllegalArgumentException("n must be 2 or 3");
        int length = LABELS * n;
        int[] used = new int[LABELS+1], next = new int[length+1], chosen = new int[length];
        int[][] action = new int[LABELS+1][LABELS+1];
        for (int i = 0; i <= LABELS; i++) action[i][i] = 1;
        long[] row = new long[n];
        long leaves = 0, prefixes = 1;
        int depth = 0;
        next[0] = 1;
        while (true) {
            if (depth == length) {
                leaves++;
                int target = endpoint(action, n);
                if (target >= 0) row[target]++;
            } else {
                int label = next[depth];
                while (label <= LABELS && used[label] == n) label++;
                if (label <= LABELS) {
                    next[depth] = label + 1;
                    chosen[depth] = label;
                    used[label]++;
                    shear(action, label, 1);
                    next[++depth] = 1;
                    prefixes++;
                    continue;
                }
            }
            if (depth == 0) break;
            int label = chosen[--depth];
            shear(action, label, -1);
            used[label]--;
        }
        long mass = factorial(length);
        for (int i = 0; i < LABELS; i++) mass /= factorial(n);
        if (leaves != mass) throw new IllegalStateException("incomplete multinomial census");
        // Pop/push are inverses. At exit all dirty basis rows must be the identity.
        for (int i = 0; i <= LABELS; i++)
            for (int j = 0; j <= LABELS; j++)
                if (action[i][j] != (i == j ? 1 : 0)) throw new IllegalStateException("undo mismatch");
        return "{\"n\":" + n + ",\"leaves\":" + leaves + ",\"prefixes\":" + prefixes
                + ",\"row\":" + Arrays.toString(row) + "}";
    }

    public static void main(String[] args) {
        System.out.println("[" + enumerate(2) + "," + enumerate(3) + "]");
    }
}
