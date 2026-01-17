#TODO Переделать способ передачи информации о видении и raycast точках
# через DTO а не через глобальный синглтон.
# Этот способ передачи информации о видении и raycast точках - кривоватый
class Debugger:
    _instance = None
    _debug_data = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def set(self, key, value):
        self._debug_data[key] = value
    
    def get(self, key):
        return self._debug_data.get(key)
    
    def log(self, message):
        print(f"[DEBUG] {message}")

# Глобальный инстанс
debug = Debugger()

