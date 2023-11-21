class Caretaker:
    def __init__(self, initial_memento):
        self.history = [initial_memento]
        self.current_state = 0

    def undo(self):
        self.current_state = self.current_state - 1 if self.current_state > 0 else 0
        return self.history[self.current_state]

    def redo(self):
        self.current_state = self.current_state + 1 if self.current_state < len(self.history) - 1 else self.history - 1
        return self.history[self.current_state]

    def add_memento(self, memento):
        if self.current_state < len(self.history) - 1:
            del self.history[self.current_state:]

        self.history.append(memento)
        self.current_state = len(self.history) - 1


