ScandirIterator_closedir(ScandirIterator *iterator)
{
    DIR *dirp = iterator->dirp;

    if (!dirp)
        return;

    iterator->dirp = NULL;
    Py_BEGIN_ALLOW_THREADS
#ifdef HAVE_FDOPENDIR
    if (iterator->path.fd != -1)
        rewinddir(dirp);
#endif
    closedir(dirp);
    Py_END_ALLOW_THREADS
    return;
}
