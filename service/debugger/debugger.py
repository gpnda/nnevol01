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




# Использование:
# ------------------------------------------------------
# from debugger import debug
# class ServiceA:
#     def process(self):
#         debug.set("last_user", "john")
#         debug.log("ServiceA started")
# ------------------------------------------------------
# from debugger import debug
# class ServiceB:
#     def validate(self):
#         user = debug.get("last_user")
#         debug.log(f"Validating user: {user}")