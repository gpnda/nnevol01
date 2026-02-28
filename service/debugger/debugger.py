#TODO Переделать способ передачи информации о видении и raycast точках
# через DTO а не через глобальный синглтон.
# Этот способ передачи информации о видении и raycast точках - кривоватый
class Debugger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._debug_data = {}
            self._initialized = True
    
    def set(self, key, value):
        self._debug_data[key] = value
    
    def get(self, key):
        return self._debug_data.get(key)

    def clear(self):
        self._debug_data.clear()
    
    def log(self, message):
        print(f"[DEBUG] {message}")

# Глобальный инстанс
debug = Debugger()

