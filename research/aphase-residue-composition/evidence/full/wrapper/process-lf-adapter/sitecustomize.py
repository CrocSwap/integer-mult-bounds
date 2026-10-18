from pathlib import Path
_original_write_text = Path.write_text
def _task_write_text(self, data, encoding=None, errors=None, newline=None):
    return _original_write_text(self, data, encoding=encoding, errors=errors,
                                newline='\n' if newline is None else newline)
Path.write_text = _task_write_text
