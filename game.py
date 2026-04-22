import random
from typing import List, Tuple, Optional, Set

class GameState:
    def __init__(self, n: int = 5):
        self.n = n
        self.cows: List[Tuple[int, int]] = []
        self.colors: List[List[int]] = []
        self.player_marks: List[List[Optional[str]]] = []
        self.right_marks: List[List[bool]] = []
        self.errors: int = 0
        self.game_over: bool = False
        self.won: bool = False
        self.generate_game()

    def generate_game(self):
        for _ in range(100):
            cows = self._generate_cows()
            colors = self._generate_colors(cows)
            if self._has_unique_solution(cows, colors):
                self.cows = cows
                self.colors = colors
                self.player_marks = [[None for _ in range(self.n)] for _ in range(self.n)]
                self.right_marks = [[False for _ in range(self.n)] for _ in range(self.n)]
                return
        raise Exception("Failed to generate game after 100 attempts")

    def _generate_cows(self) -> List[Tuple[int, int]]:
        def backtrack(row: int, placed: List[Tuple[int, int]]) -> Optional[List[Tuple[int, int]]]:
            if row == self.n:
                return placed[:]
            
            cols = list(range(self.n))
            random.shuffle(cols)
            
            for col in cols:
                if self._is_safe(row, col, placed):
                    placed.append((row, col))
                    result = backtrack(row + 1, placed)
                    if result:
                        return result
                    placed.pop()
            return None
        
        result = backtrack(0, [])
        return result if result else []

    def _is_safe(self, row: int, col: int, placed: List[Tuple[int, int]]) -> bool:
        for r, c in placed:
            if c == col:
                return False
            if abs(r - row) <= 1 and abs(c - col) <= 1:
                return False
        return True

    def _generate_colors(self, cows: List[Tuple[int, int]]) -> List[List[int]]:
        colors = [[-1 for _ in range(self.n)] for _ in range(self.n)]
        
        for i, (r, c) in enumerate(cows):
            colors[r][c] = i
        
        for _ in range(self.n * self.n):
            colored = [(r, c) for r in range(self.n) for c in range(self.n) if colors[r][c] >= 0]
            random.shuffle(colored)
            
            for r, c in colored:
                color = colors[r][c]
                neighbors = [(r+dr, c+dc) for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)] 
                             if 0 <= r+dr < self.n and 0 <= c+dc < self.n]
                random.shuffle(neighbors)
                
                for nr, nc in neighbors:
                    if colors[nr][nc] == -1:
                        colors[nr][nc] = color
                        break
            
            if all(colors[r][c] >= 0 for r in range(self.n) for c in range(self.n)):
                break
        
        return colors

    def _has_unique_solution(self, cows: List[Tuple[int, int]], colors: List[List[int]]) -> bool:
        solutions = self._find_all_solutions(colors)
        return len(solutions) == 1 and solutions[0] == set(cows)

    def _find_all_solutions(self, colors: List[List[int]]) -> List[Set[Tuple[int, int]]]:
        solutions = []
        
        color_cells = {}
        for r in range(self.n):
            for c in range(self.n):
                color = colors[r][c]
                if color not in color_cells:
                    color_cells[color] = []
                color_cells[color].append((r, c))
        
        colors_list = list(color_cells.keys())
        colors_list.sort()
        
        def backtrack(color_idx: int, placed: Set[Tuple[int, int]], 
                     used_rows: Set[int], used_cols: Set[int]):
            if color_idx == len(colors_list):
                solutions.append(placed.copy())
                return
            
            if len(solutions) >= 2:
                return
            
            color = colors_list[color_idx]
            cells = color_cells[color]
            
            for r, c in cells:
                if r in used_rows or c in used_cols:
                    continue
                
                if any(abs(pr - r) <= 1 and abs(pc - c) <= 1 for pr, pc in placed):
                    continue
                
                placed.add((r, c))
                used_rows.add(r)
                used_cols.add(c)
                
                backtrack(color_idx + 1, placed, used_rows, used_cols)
                
                placed.remove((r, c))
                used_rows.remove(r)
                used_cols.remove(c)
        
        backtrack(0, set(), set(), set())
        return solutions

    def get_color(self, row: int, col: int) -> int:
        return self.colors[row][col]

    def mark_cow(self, row: int, col: int) -> bool:
        if self.game_over:
            return False
        if self.player_marks[row][col] is not None:
            return False
        if self.right_marks[row][col]:
            return False
        
        is_cow = (row, col) in self.cows
        self.player_marks[row][col] = 'cow' if is_cow else 'wrong'
        
        if not is_cow:
            self.errors += 1
            if self.errors >= 3:
                self.game_over = True
                self.won = False
        else:
            all_found = all((r, c) in self.cows for r in range(self.n) for c in range(self.n) 
                           if self.player_marks[r][c] == 'cow')
            cows_marked = sum(1 for r in range(self.n) for c in range(self.n) 
                              if self.player_marks[r][c] == 'cow')
            if cows_marked == self.n:
                self.game_over = True
                self.won = True
        
        return True

    def mark_not_cow(self, row: int, col: int) -> bool:
        if self.game_over:
            return False
        if self.player_marks[row][col] is not None:
            return False
        
        self.right_marks[row][col] = not self.right_marks[row][col]
        return True

    def get_mark(self, row: int, col: int) -> Optional[str]:
        if self.player_marks[row][col] is not None:
            return self.player_marks[row][col]
        if self.right_marks[row][col]:
            return 'not_cow'
        return None

    def is_game_over(self) -> bool:
        return self.game_over

    def is_won(self) -> bool:
        return self.won

    def get_errors(self) -> int:
        return self.errors

    def get_remaining_cows(self) -> int:
        found = sum(1 for r in range(self.n) for c in range(self.n) 
                   if self.player_marks[r][c] == 'cow')
        return self.n - found

    def reveal_answer(self):
        self.game_over = True
        for r, c in self.cows:
            if self.player_marks[r][c] is None:
                self.player_marks[r][c] = 'cow'
