"""
Минимальная заглушка для Renderer.
"""

class Renderer:
    def __init__(self, world, app):
        self.world = world
        self.app = app
        self._variables = {}
        self._function_keys = {}
        

    
    def add_variable(self, name, initial_value, var_type, min_val=0.0, max_val=1.0, on_change=None):
        """Добавляет переменную в панель управления (заглушка)."""
        self._variables[name] = {
            'value': initial_value,
            'on_change': on_change
        }
        # Вызываем callback с начальным значением
        if on_change:
            on_change(initial_value)
    
    def add_function_key(self, key, description, callback):
        """Заглушка для add_function_key"""
        print(f"Added function key: {key}")
    
    def draw(self):
        """Заглушка для draw"""
        print("population: " +str( len(self.world.creatures)) )
        pass
    
    def control_run(self):
        """Заглушка для control_run"""
        # Простая логика для выхода - по таймеру
        if not hasattr(self, '_counter'):
            self._counter = 0
        self._counter += 1
        
        if self._counter > 1000:  # Выход после 1000 итераций
            self.app.terminate()
