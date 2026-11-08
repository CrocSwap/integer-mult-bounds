os_close_impl(PyObject *module, int fd)
/*[clinic end generated code: output=2fe4e93602822c14 input=2bc42451ca5c3223]*/
{
    int res;
    /* We do not want to retry upon EINTR: see http://lwn.net/Articles/576478/
     * and http://linux.derkeiler.com/Mailing-Lists/Kernel/2005-09/3000.html
     * for more details.
     */
    Py_BEGIN_ALLOW_THREADS
    _Py_BEGIN_SUPPRESS_IPH
    res = close(fd);
    _Py_END_SUPPRESS_IPH
    Py_END_ALLOW_THREADS
    if (res < 0)
        return posix_error();
    Py_RETURN_NONE;
}
