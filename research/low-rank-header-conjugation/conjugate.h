/* Low-rank conjugation kernel, produced by Nick Petalas. Apache-2.0.
 * Included after the retained engine's field tables and Mat declaration.
 * Preconditions: g*gi=I; request is one of its eight canonical requests.
 */
static void conjugated_request(Mat g, Mat gi, int request, Mat out) {
    for (int i = 0; i < m; i++) {
        for (int j = 0; j < m; j++) {
            int value;
            if (request < 4) {
                int product = MUL[g[i][request]][gi[request][j]];
                value = ADD[i == j][NEG[product]];
            } else if (request == 4) {
                int dual = ADD[gi[0][j]][gi[1][j]];
                value = ADD[i == j][NEG[MUL[g[i][0]][dual]]];
            } else if (request < 7) {
                int coordinate = request - 5;
                value = MUL[g[i][coordinate]][gi[coordinate][j]];
            } else {
                value = ADD[MUL[g[i][0]][gi[0][j]]]
                           [MUL[g[i][1]][gi[1][j]]];
            }
            out[i][j] = value;
        }
    }
}
