# ErrMap

A tree-style Python error formatter that replaces the default traceback printer with a clean, colour-coded call tree.

```
[ERR-MAP] Traceback detected
 root
 └── main_loop (line 12)
      > game_update()
 │    └── game_update (line 9)
           > physics_calc()
 │    │    └── physics_calc (line 6)
               > return 1 / 0

ZeroDivisionError: division by zero
```

---

## Install

```bash
pip install errmap
```

---

## Usage

```python
from errmap import ErrMap

errmap = ErrMap()
errmap.install()
```

That's it. From that point on any unhandled exception will print as a tree instead of the default traceback.

---

## API

### `ErrMap()`
Creates a new ErrMap instance.

### `errmap.install()`
Replaces `sys.excepthook` with the tree formatter.

### `errmap.active`
Set to `False` to temporarily disable ErrMap and fall back to the default traceback printer.

```python
errmap.active = False  # default traceback
errmap.active = True   # tree formatter
```

---

## License

MIT
