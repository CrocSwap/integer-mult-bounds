#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdint.h>
#include <limits.h>

/* This module is deliberately bounded. Unsupported inputs return the sentinel
 * NotImplemented; the Python binder calls the unchanged source implementation.
 * No Python integer is truncated, and the GIL remains held for each bounded call.
 */
_Static_assert(sizeof(unsigned long long) * CHAR_BIT == 64,
               "This finite backend requires 64-bit unsigned long long");

/* Read exact dict values in their insertion order. Keys are not observed by the
 * original two methods either. Return 1 for supported inputs, 0 for fallback,
 * and -1 for a genuine Python error. No caller object is changed.
 */
static int read_vectors(PyObject *basis, uint64_t vectors[64], Py_ssize_t *count) {
    Py_ssize_t position = 0;
    Py_ssize_t length;
    Py_ssize_t at = 0;
    PyObject *key;
    PyObject *value;
    if (!PyDict_CheckExact(basis)) return 0;
    length = PyDict_Size(basis);
    if (length < 0) return -1;
    if (length > 64) return 0;
    while (PyDict_Next(basis, &position, &key, &value)) {
        unsigned long long converted;
        (void)key;
        if (!PyLong_CheckExact(value)) return 0;
        converted = PyLong_AsUnsignedLongLong(value);
        if (PyErr_Occurred()) {
            if (PyErr_ExceptionMatches(PyExc_OverflowError)) {
                PyErr_Clear();
                return 0;
            }
            return -1;
        }
        if (at >= length) {
            PyErr_SetString(PyExc_RuntimeError, "basis size changed during conversion");
            return -1;
        }
        vectors[at++] = (uint64_t)converted;
    }
    if (at != length) {
        PyErr_SetString(PyExc_RuntimeError, "basis size changed during conversion");
        return -1;
    }
    *count = length;
    return 1;
}

/* XOR folding preserves parity; 0x6996 encodes parity of the low four bits. */
static unsigned parity64(uint64_t x) {
    x ^= x >> 32;
    x ^= x >> 16;
    x ^= x >> 8;
    x ^= x >> 4;
    return (unsigned)((UINT64_C(0x6996) >> (x & UINT64_C(15))) & UINT64_C(1));
}

/* Only the scalar rank is observed. Forward elimination is sufficient. */
static Py_ssize_t binary_rank(uint64_t rows[64], Py_ssize_t n) {
    Py_ssize_t rank = 0;
    unsigned column;
    for (column = 0; column < 64 && rank < n; ++column) {
        uint64_t bit = UINT64_C(1) << column;
        Py_ssize_t pivot = rank;
        Py_ssize_t i;
        uint64_t temp;
        while (pivot < n && !(rows[pivot] & bit)) ++pivot;
        if (pivot == n) continue;
        temp = rows[rank]; rows[rank] = rows[pivot]; rows[pivot] = temp;
        for (i = rank + 1; i < n; ++i) {
            if (rows[i] & bit) rows[i] ^= rows[rank];
        }
        ++rank;
    }
    return rank;
}

/* Return (the original ordered Gram rows, its exact rank), so the same full
 * rank transcript can be recorded by both benchmark arms. The public Label
 * method still returns exactly bool, including True for the empty basis.
 */
static PyObject *gram_rank(PyObject *self, PyObject *args) {
    PyObject *basis;
    uint64_t vectors[64];
    uint64_t rows[64];
    uint64_t work[64];
    Py_ssize_t n = 0;
    Py_ssize_t i;
    Py_ssize_t j;
    Py_ssize_t rank;
    int accepted;
    PyObject *gram;
    PyObject *rank_value;
    PyObject *answer;
    (void)self;
    if (!PyArg_ParseTuple(args, "O:gram_rank", &basis)) return NULL;
    accepted = read_vectors(basis, vectors, &n);
    if (accepted < 0) return NULL;
    if (!accepted) Py_RETURN_NOTIMPLEMENTED;
    for (i = 0; i < n; ++i) {
        uint64_t row = 0;
        for (j = 0; j < n; ++j) {
            row |= (uint64_t)parity64(vectors[i] & vectors[j]) << (unsigned)j;
        }
        rows[i] = row;
        work[i] = row;
    }
    rank = binary_rank(work, n);
    gram = PyTuple_New(n);
    if (gram == NULL) return NULL;
    for (i = 0; i < n; ++i) {
        PyObject *value = PyLong_FromUnsignedLongLong((unsigned long long)rows[i]);
        if (value == NULL) { Py_DECREF(gram); return NULL; }
        PyTuple_SET_ITEM(gram, i, value);
    }
    rank_value = PyLong_FromSsize_t(rank);
    if (rank_value == NULL) { Py_DECREF(gram); return NULL; }
    answer = PyTuple_New(2);
    if (answer == NULL) { Py_DECREF(gram); Py_DECREF(rank_value); return NULL; }
    PyTuple_SET_ITEM(answer, 0, gram);
    PyTuple_SET_ITEM(answer, 1, rank_value);
    return answer;
}

/* Literal ordered augmented-row algorithm from Label.complement_in.
 * low k bits: pairings against self, in self.basis insertion order.
 * high n bits: coefficient identity for other.basis, in its insertion order.
 * The first available pivot and ALL-row clearing match the source exactly;
 * output rows stay in the identical order and are not re-canonicalized.
 */
static PyObject *complement(PyObject *self, PyObject *args) {
    PyObject *small;
    PyObject *big;
    uint64_t us[64];
    uint64_t vs[64];
    uint64_t rows[64];
    Py_ssize_t k = 0;
    Py_ssize_t n = 0;
    Py_ssize_t i;
    Py_ssize_t j;
    Py_ssize_t column;
    Py_ssize_t rank = 0;
    int accepted;
    uint64_t low_mask;
    PyObject *out;
    (void)self;
    if (!PyArg_ParseTuple(args, "OO:complement", &small, &big)) return NULL;
    accepted = read_vectors(big, vs, &n);
    if (accepted < 0) return NULL;
    if (!accepted) Py_RETURN_NOTIMPLEMENTED;
    accepted = read_vectors(small, us, &k);
    if (accepted < 0) return NULL;
    if (!accepted || k + n > 64) Py_RETURN_NOTIMPLEMENTED;
    for (i = 0; i < n; ++i) {
        uint64_t row = UINT64_C(1) << (unsigned)(k + i);
        for (j = 0; j < k; ++j) {
            row |= (uint64_t)parity64(vs[i] & us[j]) << (unsigned)j;
        }
        rows[i] = row;
    }
    for (column = 0; column < k; ++column) {
        uint64_t bit = UINT64_C(1) << (unsigned)column;
        Py_ssize_t pivot = rank;
        uint64_t temp;
        while (pivot < n && !(rows[pivot] & bit)) ++pivot;
        if (pivot == n) continue;
        temp = rows[rank]; rows[rank] = rows[pivot]; rows[pivot] = temp;
        for (i = 0; i < n; ++i) {
            if (i != rank && (rows[i] & bit)) rows[i] ^= rows[rank];
        }
        ++rank;
    }
    low_mask = k == 64 ? UINT64_MAX : ((UINT64_C(1) << (unsigned)k) - UINT64_C(1));
    out = PyList_New(n - rank);
    if (out == NULL) return NULL;
    for (i = rank; i < n; ++i) {
        uint64_t x = 0;
        PyObject *value;
        if (rows[i] & low_mask) {
            Py_DECREF(out);
            PyErr_SetString(PyExc_AssertionError, "");
            return NULL;
        }
        for (j = 0; j < n; ++j) {
            if ((rows[i] >> (unsigned)(k + j)) & UINT64_C(1)) x ^= vs[j];
        }
        value = PyLong_FromUnsignedLongLong((unsigned long long)x);
        if (value == NULL) { Py_DECREF(out); return NULL; }
        PyList_SET_ITEM(out, i - rank, value);
    }
    return out;
}

static PyMethodDef methods[] = {
    {"gram_rank", gram_rank, METH_VARARGS, "Ordered GF(2) Gram rows and exact rank, or NotImplemented."},
    {"complement", complement, METH_VARARGS, "Exact ordered GF(2) complement vectors, or NotImplemented."},
    {NULL, NULL, 0, NULL}
};
static struct PyModuleDef module_definition = {
    PyModuleDef_HEAD_INIT, "_packed_gf2", "Bounded exact GF(2) verification kernels.",
    -1, methods, NULL, NULL, NULL, NULL
};
PyMODINIT_FUNC PyInit__packed_gf2(void) {
    return PyModule_Create(&module_definition);
}
