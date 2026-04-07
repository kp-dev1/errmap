import sys
import traceback
import json

class ErrMap:
    __slots__ = ["branch", "vertical", "active", "_errors", "_filepath"]
    def __init__(self, filepath=None):
        self.branch = " └── "
        self.vertical = " │   "
        self.active = True
        self._errors = []
        self._filepath = filepath

    def _build_json_data(self, etype, value, tb):
        """Convert error to JSON-serializable dict"""
        frames = traceback.extract_tb(tb)

        call_tree = []
        for i, frame in enumerate(frames):
            call_tree.append({
                "name": frame.name,
                "line": frame.lineno,
                "code": frame.line.strip() if frame.line else "",
                "is_error_frame": (i == len(frames) - 1)
            })

        return {
            "error_type": etype.__name__,
            "error_message": str(value),
            "call_tree": call_tree
        }

    def _draw_tree(self, etype, value, tb):
        self._errors.append(self._build_json_data(etype, value, tb))
        
        if self._filepath:
            self._auto_save()
        
        frames = traceback.extract_tb(tb)
        totalframes = len(frames)
        
        print("\n\033[91m[ERR-MAP] Traceback detected\033[0m")
        print(" root")

        for i, frame in enumerate(frames):
            indent = self.vertical * i
            is_last = (i == totalframes - 1)
            if not is_last:
                print(f"{indent}{self.branch}\033[92m{frame.name}\033[0m (line {frame.lineno})")
                print(f"{indent}     \033[90m> {frame.line}\033[0m")
            else:
                print(f"{indent}{self.branch}\033[91m{frame.name}\033[0m (line {frame.lineno})")
                print(f"{indent}     \033[90m> {frame.line}\033[0m")

        print(f"\n\033[91m{etype.__name__}: {value}\033[0m\n")

    def _auto_save(self):
        """Auto-save errors to the configured filepath"""
        if self._filepath:
            with open(self._filepath, 'w') as f:
                json.dump(self._errors, f, indent=2, default=str)

    def install(self):
        """ Replaces the default Python error printer with yours """
        def hook(etype, value, tb):
            if self.active:
                self._draw_tree(etype, value, tb)
            else:
                sys.__excepthook__(etype, value, tb)
        
        sys.excepthook = hook

    def save_to_json(self, filepath):
        """Save all captured errors to a JSON file"""
        if not self._errors:
            print("[ERR-MAP] No errors to save. Has an exception occurred?")
            return
        
        with open(filepath, 'w') as f:
            json.dump(self._errors, f, indent=2, default=str)
