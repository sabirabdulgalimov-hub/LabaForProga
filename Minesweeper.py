import pygame
import random
import sys
from typing import List, Tuple, Optional

class Minesweeper:
    def __init__(self):
        pygame.init()
        
        # Настройки по умолчанию
        self.difficulty = "medium"
        self.set_difficulty(self.difficulty)
        
        # Получаем размеры экрана после установки сложности
        self.width = self.cols * self.cell_size
        self.height = self.rows * self.cell_size + 50
        
        # Цвета
        self.BG_COLOR = (240, 240, 240)
        self.GRID_COLOR = (180, 180, 180)
        self.HIDDEN_COLOR = (200, 200, 200)
        self.REVEALED_COLOR = (220, 220, 220)
        self.MINE_COLOR = (255, 0, 0)
        self.EXPLODED_MINE_COLOR = (255, 100, 100)
        self.FLAG_COLOR = (0, 0, 255)
        self.WRONG_FLAG_COLOR = (255, 0, 0)
        self.TEXT_COLORS = [
            None,  # 0 - нет цвета
            (0, 0, 255),    # 1
            (0, 128, 0),    # 2
            (255, 0, 0),    # 3
            (0, 0, 128),    # 4
            (128, 0, 0),    # 5
            (0, 128, 128),  # 6
            (0, 0, 0),      # 7
            (128, 128, 128) # 8
        ]
        
        # Создание окна во весь экран
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.FULLSCREEN)
        pygame.display.set_caption("Сапер")
        
        # Шрифты
        self.title_font = pygame.font.SysFont('Arial', 48, bold=True)
        self.font = pygame.font.SysFont('Arial', 24)
        self.small_font = pygame.font.SysFont('Arial', 18)
        
        # Состояния игры
        self.state = "menu"  # menu, game, game_over, game_won
        self.reset_game()
        
    def set_difficulty(self, difficulty):
        """Установка уровня сложности"""
        self.difficulty = difficulty
        if difficulty == "easy":
            self.rows, self.cols, self.mines_count = 9, 9, 10
        elif difficulty == "medium":
            self.rows, self.cols, self.mines_count = 16, 16, 40
        elif difficulty == "hard":
            self.rows, self.cols, self.mines_count = 16, 30, 99
        
        # Автоподбор размера клетки для полного экрана
        # Получаем размеры экрана
        screen_info = pygame.display.Info()
        screen_width = screen_info.current_w
        screen_height = screen_info.current_h
        
        max_cell_width = (screen_width - 100) // self.cols
        max_cell_height = (screen_height - 150) // self.rows
        self.cell_size = min(max_cell_width, max_cell_height, 50)  # Максимум 50px
        self.cell_size = max(self.cell_size, 20)  # Минимум 20px
        
        # Центрирование игрового поля
        self.field_width = self.cols * self.cell_size
        self.field_height = self.rows * self.cell_size
        self.field_x = (screen_width - self.field_width) // 2
        self.field_y = (screen_height - self.field_height) // 2 + 20
        
        # Обновляем размеры окна
        if hasattr(self, 'screen'):
            self.width = screen_width
            self.height = screen_height
            self.screen = pygame.display.set_mode((self.width, self.height), pygame.FULLSCREEN)
    
    # Остальные методы остаются без изменений...
    def reset_game(self):
        """Сброс игры к начальному состоянию"""
        self.board = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.revealed = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        self.flagged = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        self.mines = set()
        self.game_over = False
        self.game_won = False
        self.first_click = True
        self.mines_remaining = self.mines_count
        self.start_time = None
        self.elapsed_time = 0
        self.exploded_mine = None  # Координаты взорвавшейся мины
        
    def place_mines(self, exclude_row: int, exclude_col: int):
        """Размещение мин на поле, исключая клетку первого клика"""
        mines_placed = 0
        while mines_placed < self.mines_count:
            row = random.randint(0, self.rows - 1)
            col = random.randint(0, self.cols - 1)
            
            # Не ставим мину в клетку первого клика и вокруг нее
            if (row == exclude_row and col == exclude_col) or \
               (abs(row - exclude_row) <= 1 and abs(col - exclude_col) <= 1):
                continue
                
            if (row, col) not in self.mines:
                self.mines.add((row, col))
                self.board[row][col] = -1  # -1 означает мину
                mines_placed += 1
                
        # Подсчет чисел для всех клеток
        for row in range(self.rows):
            for col in range(self.cols):
                if self.board[row][col] != -1:
                    self.board[row][col] = self.count_adjacent_mines(row, col)
    
    def count_adjacent_mines(self, row: int, col: int) -> int:
        """Подсчет мин в соседних клетках"""
        count = 0
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                    
                r, c = row + dr, col + dc
                if 0 <= r < self.rows and 0 <= c < self.cols:
                    if (r, c) in self.mines:
                        count += 1
        return count
    
    def reveal_cell(self, row: int, col: int):
        """Открытие клетки и рекурсивное открытие пустых областей"""
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return
            
        if self.revealed[row][col] or self.flagged[row][col]:
            return
            
        self.revealed[row][col] = True
        
        # Если открыли мину - игра окончена
        if (row, col) in self.mines:
            self.game_over = True
            self.exploded_mine = (row, col)
            self.state = "game_over"
            return
            
        # Рекурсивно открываем соседние клетки если текущая пустая
        if self.board[row][col] == 0:
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    self.reveal_cell(row + dr, col + dc)
    
    def toggle_flag(self, row: int, col: int):
        """Установка или снятие флажка"""
        if not self.revealed[row][col] and not self.game_over and not self.game_won:
            self.flagged[row][col] = not self.flagged[row][col]
            if self.flagged[row][col]:
                self.mines_remaining -= 1
            else:
                self.mines_remaining += 1
    
    def check_win(self) -> bool:
        """Проверка условия победы"""
        for row in range(self.rows):
            for col in range(self.cols):
                # Если есть неоткрытая клетка без мины - игра не выиграна
                if not self.revealed[row][col] and (row, col) not in self.mines:
                    return False
        return True
    
    def handle_game_click(self, pos: Tuple[int, int], right_click: bool = False):
        """Обработка клика мыши в игровом режиме"""
        if self.game_over or self.game_won:
            return
            
        x, y = pos
        
        # Проверка клика по игровому полю
        if (self.field_x <= x < self.field_x + self.field_width and 
            self.field_y <= y < self.field_y + self.field_height):
            
            row = (y - self.field_y) // self.cell_size
            col = (x - self.field_x) // self.cell_size
            
            if 0 <= row < self.rows and 0 <= col < self.cols:
                if right_click:
                    self.toggle_flag(row, col)
                else:
                    if self.first_click:
                        self.first_click = False
                        self.place_mines(row, col)
                        self.start_time = pygame.time.get_ticks()
                    
                    if not self.flagged[row][col]:
                        self.reveal_cell(row, col)
                        
                        # Проверка на выигрыш
                        if not self.game_over and self.check_win():
                            self.game_won = True
                            self.state = "game_won"
                            self.elapsed_time = (pygame.time.get_ticks() - self.start_time) // 1000
    
    def draw_menu(self):
        """Отрисовка главного меню"""
        self.screen.fill(self.BG_COLOR)
        
        # Заголовок
        title = self.title_font.render("САПЕР", True, (0, 0, 0))
        title_rect = title.get_rect(center=(self.width // 2, self.height // 4))
        self.screen.blit(title, title_rect)
        
        # Кнопки выбора сложности
        button_width, button_height = 350, 50
        button_margin = 20
        
        difficulties = [
            ("ЛЕГКИЙ (9x9, 10 мин)", "easy"),
            ("СРЕДНИЙ (16x16, 40 мин)", "medium"),
            ("СЛОЖНЫЙ (16x30, 99 мин)", "hard"),
            ("ВЫХОД", "exit")
        ]
        
        for i, (text, difficulty) in enumerate(difficulties):
            button_rect = pygame.Rect(
                self.width // 2 - button_width // 2,
                self.height // 2 + i * (button_height + button_margin),
                button_width,
                button_height
            )
            
            # Проверка наведения мыши
            mouse_pos = pygame.mouse.get_pos()
            is_hovered = button_rect.collidepoint(mouse_pos)
            
            # Цвет кнопки
            if difficulty == self.difficulty:
                color = (100, 150, 255)  # Выбранная сложность
            elif is_hovered:
                color = (200, 200, 200)  # Наведение
            else:
                color = (150, 150, 150)  # Обычная
            
            pygame.draw.rect(self.screen, color, button_rect, border_radius=10)
            pygame.draw.rect(self.screen, (50, 50, 50), button_rect, 2, border_radius=10)
            
            button_text = self.font.render(text, True, (0, 0, 0))
            text_rect = button_text.get_rect(center=button_rect.center)
            self.screen.blit(button_text, text_rect)
    
    def draw_game(self):
        """Отрисовка игрового поля"""
        self.screen.fill(self.BG_COLOR)
        
        # Панель статуса
        status_height = 60
        status_bg = pygame.Rect(0, 0, self.width, status_height)
        pygame.draw.rect(self.screen, (220, 220, 220), status_bg)
        pygame.draw.line(self.screen, self.GRID_COLOR, (0, status_height), 
                        (self.width, status_height), 2)
        
        # Отображение оставшихся мин
        mines_text = self.font.render(f'Мины: {self.mines_remaining}', True, (0, 0, 0))
        self.screen.blit(mines_text, (50, 20))
        
        # Отображение времени
        if self.start_time and not self.game_over and not self.game_won:
            self.elapsed_time = (pygame.time.get_ticks() - self.start_time) // 1000
        time_text = self.font.render(f'Время: {self.elapsed_time} сек', True, (0, 0, 0))
        self.screen.blit(time_text, (self.width // 2 - 50, 20))
        
        # Кнопка возврата в меню
        menu_button = pygame.Rect(self.width - 150, 15, 120, 30)
        pygame.draw.rect(self.screen, (200, 200, 200), menu_button, border_radius=5)
        pygame.draw.rect(self.screen, (100, 100, 100), menu_button, 2, border_radius=5)
        menu_text = self.small_font.render('В МЕНЮ', True, (0, 0, 0))
        self.screen.blit(menu_text, (menu_button.x + 20, menu_button.y + 8))
        
        # Отрисовка игрового поля
        for row in range(self.rows):
            for col in range(self.cols):
                x = self.field_x + col * self.cell_size
                y = self.field_y + row * self.cell_size
                rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
                
                if self.revealed[row][col]:
                    # Открытая клетка
                    pygame.draw.rect(self.screen, self.REVEALED_COLOR, rect)
                    
                    if (row, col) in self.mines:
                        # Мина
                        if self.game_over and (row, col) == self.exploded_mine:
                            # Взорвавшаяся мина - красный фон
                            pygame.draw.rect(self.screen, self.EXPLODED_MINE_COLOR, rect)
                        
                        mine_center = (x + self.cell_size // 2, y + self.cell_size // 2)
                        pygame.draw.circle(self.screen, self.MINE_COLOR, mine_center, self.cell_size // 3)
                    elif self.board[row][col] > 0:
                        # Число
                        number_text = self.font.render(str(self.board[row][col]), True, 
                                                    self.TEXT_COLORS[self.board[row][col]])
                        text_rect = number_text.get_rect(center=(x + self.cell_size // 2, 
                                                                y + self.cell_size // 2))
                        self.screen.blit(number_text, text_rect)
                else:
                    # Скрытая клетка
                    pygame.draw.rect(self.screen, self.HIDDEN_COLOR, rect)
                    
                    if self.flagged[row][col]:
                        # Флажок
                        flag_points = [
                            (x + self.cell_size // 4, y + self.cell_size // 4),
                            (x + self.cell_size * 3 // 4, y + self.cell_size // 2),
                            (x + self.cell_size // 4, y + self.cell_size * 3 // 4)
                        ]
                        pygame.draw.polygon(self.screen, self.FLAG_COLOR, flag_points)
                
                # Сетка
                pygame.draw.rect(self.screen, self.GRID_COLOR, rect, 1)
        
        # Показ всех мин при проигрыше
        if self.game_over:
            for row, col in self.mines:
                if not self.revealed[row][col] and not self.flagged[row][col]:
                    x = self.field_x + col * self.cell_size
                    y = self.field_y + row * self.cell_size
                    rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
                    
                    mine_center = (x + self.cell_size // 2, y + self.cell_size // 2)
                    pygame.draw.circle(self.screen, self.MINE_COLOR, mine_center, self.cell_size // 3)
            
            # Показ неправильных флажков
            for row in range(self.rows):
                for col in range(self.cols):
                    if self.flagged[row][col] and (row, col) not in self.mines:
                        x = self.field_x + col * self.cell_size
                        y = self.field_y + row * self.cell_size
                        rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
                        
                        # Красный крестик поверх флажка
                        pygame.draw.line(self.screen, self.WRONG_FLAG_COLOR,
                                        (x + 5, y + 5),
                                        (x + self.cell_size - 5, y + self.cell_size - 5), 2)
                        pygame.draw.line(self.screen, self.WRONG_FLAG_COLOR,
                                        (x + self.cell_size - 5, y + 5),
                                        (x + 5, y + self.cell_size - 5), 2)
        
        # Сообщения о результате игры
        if self.game_over:
            self.show_message("ИГРА ОКОНЧЕНА! ВЫ ПРОИГРАЛИ!", (255, 0, 0))
        elif self.game_won:
            self.show_message(f"ПОЗДРАВЛЯЕМ! ВЫ ВЫИГРАЛИ ЗА {self.elapsed_time} СЕКУНД!", (0, 128, 0))
    
    def show_message(self, text: str, color: Tuple[int, int, int]):
        """Показать сообщение поверх игрового поля"""
        message_font = pygame.font.SysFont('Arial', 32, bold=True)
        message_text = message_font.render(text, True, color)
        text_rect = message_text.get_rect(center=(self.width // 2, 80))
        
        # Полупрозрачный фон
        s = pygame.Surface((self.width, 100), pygame.SRCALPHA)
        s.fill((255, 255, 255, 200))
        self.screen.blit(s, (0, 30))
        
        self.screen.blit(message_text, text_rect)
        
        # Кнопка новой игры
        button_rect = pygame.Rect(self.width // 2 - 100, 120, 200, 40)
        pygame.draw.rect(self.screen, (150, 150, 150), button_rect, border_radius=5)
        pygame.draw.rect(self.screen, (50, 50, 50), button_rect, 2, border_radius=5)
        
        button_text = self.font.render("НОВАЯ ИГРА", True, (0, 0, 0))
        button_text_rect = button_text.get_rect(center=button_rect.center)
        self.screen.blit(button_text, button_text_rect)
    
    def handle_menu_click(self, pos: Tuple[int, int]):
        """Обработка клика в меню"""
        x, y = pos
        
        button_width, button_height = 200, 50
        button_margin = 20
        
        difficulties = ["easy", "medium", "hard", "exit"]
        
        for i, difficulty in enumerate(difficulties):
            button_rect = pygame.Rect(
                self.width // 2 - button_width // 2,
                self.height // 2 + i * (button_height + button_margin),
                button_width,
                button_height
            )
            
            if button_rect.collidepoint(x, y):
                if difficulty == "exit":
                    pygame.quit()
                    sys.exit()
                else:
                    self.set_difficulty(difficulty)
                    self.reset_game()
                    self.state = "game"
    
    def handle_game_over_click(self, pos: Tuple[int, int]):
        """Обработка клика в состоянии game_over или game_won"""
        x, y = pos
        
        # Кнопка новой игры
        button_rect = pygame.Rect(self.width // 2 - 100, 120, 200, 40)
        if button_rect.collidepoint(x, y):
            self.reset_game()
            self.state = "game"
    
    def run(self):
        """Основной игровой цикл"""
        clock = pygame.time.Clock()
        
        try:
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            if self.state == "game":
                                self.state = "menu"
                            else:
                                pygame.quit()
                                sys.exit()
                    
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:  # Левая кнопка мыши
                            if self.state == "menu":
                                self.handle_menu_click(event.pos)
                            elif self.state == "game":
                                # Проверка клика по кнопке меню
                                menu_button = pygame.Rect(self.width - 150, 15, 120, 30)
                                if menu_button.collidepoint(event.pos):
                                    self.state = "menu"
                                else:
                                    self.handle_game_click(event.pos)
                            elif self.state in ["game_over", "game_won"]:
                                self.handle_game_over_click(event.pos)
                                
                        elif event.button == 3:  # Правая кнопка мыши
                            if self.state == "game":
                                self.handle_game_click(event.pos, right_click=True)
                
                # Отрисовка в зависимости от состояния
                if self.state == "menu":
                    self.draw_menu()
                elif self.state in ["game", "game_over", "game_won"]:
                    self.draw_game()
                
                pygame.display.flip()
                clock.tick(60)
                
        except Exception as e:
            print(f"Произошла ошибка: {e}")
            print("Игра будет перезапущена...")
            pygame.quit()
            # Перезапуск игры
            new_game = Minesweeper()
            new_game.run()

if __name__ == "__main__":
    try:
        game = Minesweeper()
        game.run()
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        input("Нажмите Enter для выхода...")