/* Stateless canonical complement-record encoding for the frozen H25 observer.
 * All symbols are trace-prefixed so the parent may include this source in its
 * combined extension with H25_TRACE_EMBEDDED defined. No GF(2) code is changed.
 */
#ifndef PY_SSIZE_T_CLEAN
#define PY_SSIZE_T_CLEAN
#endif
#include <Python.h>
#include <stdint.h>
#include <limits.h>
#include <string.h>

_Static_assert(sizeof(unsigned long long) * CHAR_BIT == 64,
               "H25 trace encoding requires 64-bit unsigned long long");

#define H25_TRACE_CAPACITY 8192
#define H25_TRACE_MAX_VECTOR 64

typedef struct {
    char data[H25_TRACE_CAPACITY];
    Py_ssize_t used;
} h25_trace_buffer;

/* 1 means admitted, 0 means literal-JSON fallback, -1 means genuine error.
 * Exact-type admission prevents __index__ or any other caller callback.
 * UINT64_MAX is a valid value: the error indicator, not its bits, decides.
 */
static int h25_trace_u64(PyObject *value, uint64_t *out) {
    unsigned long long converted;
    if (!PyLong_CheckExact(value)) return 0;
    converted = PyLong_AsUnsignedLongLong(value);
    if (PyErr_Occurred()) {
        if (PyErr_ExceptionMatches(PyExc_OverflowError)) {
            PyErr_Clear();
            return 0;
        }
        return -1;
    }
    *out = (uint64_t)converted;
    return 1;
}

/* Capacity checks precede every write. A rejected record exposes no bytes. */
static int h25_trace_append(h25_trace_buffer *buffer, const char *text,
                            Py_ssize_t length) {
    if (length < 0 || length > H25_TRACE_CAPACITY || buffer->used < 0 ||
        buffer->used > H25_TRACE_CAPACITY - length) return 0;
    memcpy(buffer->data + buffer->used, text, (size_t)length);
    buffer->used += length;
    return 1;
}

#define H25_TRACE_LITERAL(buffer, literal) \
    h25_trace_append((buffer), (literal), (Py_ssize_t)(sizeof(literal) - 1))

static int h25_trace_decimal(h25_trace_buffer *buffer, uint64_t value) {
    char reversed[20];
    Py_ssize_t digits = 0;
    Py_ssize_t i;
    do {
        if (digits >= (Py_ssize_t)sizeof(reversed)) return 0;
        reversed[digits++] = (char)('0' + value % UINT64_C(10));
        value /= UINT64_C(10);
    } while (value != 0);
    if (buffer->used < 0 || buffer->used > H25_TRACE_CAPACITY - digits)
        return 0;
    for (i = digits; i > 0; --i) buffer->data[buffer->used++] = reversed[i - 1];
    return 1;
}

/* Containers were admitted before this helper. Borrowed references remain
 * valid while the native call owns its arguments and holds the GIL. No Python
 * callbacks run and no reference is retained when this function returns.
 */
static int h25_trace_vector(h25_trace_buffer *buffer, PyObject *values,
                            Py_ssize_t length, int is_list) {
    Py_ssize_t i;
    for (i = 0; i < length; ++i) {
        PyObject *value = is_list ? PyList_GET_ITEM(values, i)
                                  : PyTuple_GET_ITEM(values, i);
        uint64_t converted;
        int admitted = h25_trace_u64(value, &converted);
        if (admitted != 1) return admitted;
        if (i != 0 && !H25_TRACE_LITERAL(buffer, ",")) return 0;
        if (!h25_trace_decimal(buffer, converted)) return 0;
    }
    return 1;
}

/* Fixed schema, sorted key order: call,result,us,vs; result type,values.
 * At most 192 20-digit vector values plus one 20-digit count, separators and
 * fixed ASCII punctuation fit below 8192 bytes. Checks remain mandatory.
 */
static PyObject *h25_trace_encode_record(PyObject *self,
                                         PyObject *const *args,
                                         Py_ssize_t nargs) {
    PyObject *call;
    PyObject *us;
    PyObject *vs;
    PyObject *output;
    Py_ssize_t us_length;
    Py_ssize_t vs_length;
    Py_ssize_t output_length = 0;
    uint64_t call_value;
    int admitted;
    h25_trace_buffer buffer;
    (void)self;
    if (nargs != 4) {
        PyErr_Format(PyExc_TypeError,
                     "encode_record() takes exactly 4 positional arguments (%zd given)",
                     nargs);
        return NULL;
    }
    call = args[0];
    us = args[1];
    vs = args[2];
    output = args[3];
    if (!PyTuple_CheckExact(us) || !PyTuple_CheckExact(vs) ||
        (output != Py_None && !PyList_CheckExact(output))) Py_RETURN_NOTIMPLEMENTED;
    us_length = PyTuple_GET_SIZE(us);
    vs_length = PyTuple_GET_SIZE(vs);
    if (output != Py_None) output_length = PyList_GET_SIZE(output);
    if (us_length > H25_TRACE_MAX_VECTOR || vs_length > H25_TRACE_MAX_VECTOR ||
        output_length > H25_TRACE_MAX_VECTOR) Py_RETURN_NOTIMPLEMENTED;
    admitted = h25_trace_u64(call, &call_value);
    if (admitted < 0) return NULL;
    if (!admitted) Py_RETURN_NOTIMPLEMENTED;
    buffer.used = 0;
    if (!H25_TRACE_LITERAL(&buffer, "{\"call\":")) Py_RETURN_NOTIMPLEMENTED;
    if (!h25_trace_decimal(&buffer, call_value)) Py_RETURN_NOTIMPLEMENTED;
    if (output == Py_None) {
        if (!H25_TRACE_LITERAL(&buffer, ",\"result\":{\"type\":\"None\"}"))
            Py_RETURN_NOTIMPLEMENTED;
    } else {
        if (!H25_TRACE_LITERAL(&buffer, ",\"result\":{\"type\":\"list\",\"values\":["))
            Py_RETURN_NOTIMPLEMENTED;
        admitted = h25_trace_vector(&buffer, output, output_length, 1);
        if (admitted < 0) return NULL;
        if (!admitted) Py_RETURN_NOTIMPLEMENTED;
        if (!H25_TRACE_LITERAL(&buffer, "]}")) Py_RETURN_NOTIMPLEMENTED;
    }
    if (!H25_TRACE_LITERAL(&buffer, ",\"us\":[")) Py_RETURN_NOTIMPLEMENTED;
    admitted = h25_trace_vector(&buffer, us, us_length, 0);
    if (admitted < 0) return NULL;
    if (!admitted) Py_RETURN_NOTIMPLEMENTED;
    if (!H25_TRACE_LITERAL(&buffer, "],\"vs\":[")) Py_RETURN_NOTIMPLEMENTED;
    admitted = h25_trace_vector(&buffer, vs, vs_length, 0);
    if (admitted < 0) return NULL;
    if (!admitted) Py_RETURN_NOTIMPLEMENTED;
    if (!H25_TRACE_LITERAL(&buffer, "]}\n")) Py_RETURN_NOTIMPLEMENTED;
    /* One allocation/copy; no reference to the stack buffer escapes. */
    return PyBytes_FromStringAndSize(buffer.data, buffer.used);
}

#ifndef H25_TRACE_EMBEDDED
static PyMethodDef h25_trace_methods[] = {
    {"encode_record", (PyCFunction)(void (*)(void))h25_trace_encode_record,
     METH_FASTCALL,
     "Canonical one-record ASCII JSON bytes plus LF, or NotImplemented."},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef h25_trace_module_definition = {
    PyModuleDef_HEAD_INIT,
    "_trace_encoding",
    "Bounded stateless H25 complement-record encoding.",
    -1,
    h25_trace_methods,
    NULL, NULL, NULL, NULL
};

PyMODINIT_FUNC PyInit__trace_encoding(void) {
    return PyModule_Create(&h25_trace_module_definition);
}
#endif
