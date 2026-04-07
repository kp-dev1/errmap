import sys
import traceback

class ErrMap:
    __slots__ = ["branch", "vertical", "active"]
    def __init__(self):
        self.branch = " └── "
        self.vertical = " │   "
        self.active = True

    def _draw_tree(self, etype, value, tb):
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

    def install(self):
        """ Replaces the default Python error printer with yours """
        def hook(etype, value, tb):
            if self.active:
                self._draw_tree(etype, value, tb)
            else:
                sys.__excepthook__(etype, value, tb)
        
        sys.excepthook = hook
