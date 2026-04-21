import random
from typing import List, Tuple, Optional, Set, Dict

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
        if self.n <= 5:
            self._generate_simple()
        else:
            self._generate_large()

    def _generate_simple(self):
        max_attempts = 300
        for attempt in range(max_attempts):
            cows = self._generate_cows()
            if not cows:
                continue
            
            colors = self._generate_colors_simple(cows)
            if not colors:
                continue
            
            if self._has_unique_solution(cows, colors):
                self.cows = cows
                self.colors = colors
                self._init_marks()
                return
        
        raise Exception("Failed to generate game")

    def _generate_large(self):
        max_attempts = 200
        for attempt in range(max_attempts):
            cows = self._generate_cows()
            if not cows:
                continue
            
            colors = self._generate_colors_structured(cows)
            if not colors:
                continue
            
            if self._has_unique_solution_fast(cows, colors):
                self.cows = cows
                self.colors = colors
                self._init_marks()
                return
        
        for attempt in range(100):
            cows = self._generate_cows()
            if not cows:
                continue
            
            colors = self._generate_colors_with_constraints(cows)
            if not colors:
                continue
            
            self.cows = cows
            self.colors = colors
            self._init_marks()
            return
        
        raise Exception("Failed to generate game after multiple attempts")

    def _init_marks(self):
        self.player_marks = [[None for _ in range(self.n)] for _ in range(self.n)]
        self.right_marks = [[False for _ in range(self.n)] for _ in range(self.n)]

    def _generate_cows(self) -> List[Tuple[int, int]]:
        def backtrack(row: int, placed: List[Tuple[int, int]]) -> Optional[List[Tuple[int, int]]]:
            if row == self.n:
                return placed[:]
            
            available_cols = []
            for col in range(self.n):
                if self._is_safe(row, col, placed):
                    available_cols.append(col)
            
            random.shuffle(available_cols)
            
            for col in available_cols:
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

    def _generate_colors_simple(self, cows: List[Tuple[int, int]]) -> Optional[List[List[int]]]:
        colors = [[-1 for _ in range(self.n)] for _ in range(self.n)]
        
        for i, (r, c) in enumerate(cows):
            colors[r][c] = i
        
        for _ in range(self.n * self.n * 3):
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
        
        if not all(colors[r][c] >= 0 for r in range(self.n) for c in range(self.n)):
            return None
        
        if not self._check_color_connectivity(colors):
            return None
        
        return colors

    def _generate_colors_structured(self, cows: List[Tuple[int, int]]) -> Optional[List[List[int]]]:
        colors = [[-1 for _ in range(self.n)] for _ in range(self.n)]
        
        cow_pos = {i: cows[i] for i in range(self.n)}
        
        for i, (r, c) in enumerate(cows):
            colors[r][c] = i
        
        color_rows: Dict[int, Set[int]] = {i: {cows[i][0]} for i in range(self.n)}
        color_cols: Dict[int, Set[int]] = {i: {cows[i][1]} for i in range(self.n)}
        
        uncolored = {(r, c) for r in range(self.n) for c in range(self.n) if colors[r][c] == -1}
        
        for _ in range(self.n * self.n * 2):
            if not uncolored:
                break
            
            progress = False
            
            color_list = list(range(self.n))
            random.shuffle(color_list)
            
            for color in color_list:
                cr, cc = cow_pos[color]
                
                neighbors = [
                    (cr+dr, cc+dc) 
                    for dr, dc in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]
                    if 0 <= cr+dr < self.n and 0 <= cc+dc < self.n
                    and (cr+dr, cc+dc) in uncolored
                ]
                
                if not neighbors:
                    colored_cells = [(r, c) for r in range(self.n) for c in range(self.n) 
                                     if colors[r][c] == color]
                    for r, c in colored_cells:
                        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < self.n and 0 <= nc < self.n and (nr, nc) in uncolored:
                                neighbors.append((nr, nc))
                    
                    random.shuffle(neighbors)
                
                for nr, nc in neighbors:
                    if nr not in color_rows[color] and nc not in color_cols[color]:
                        row_conflict = False
                        col_conflict = False
                        
                        for other_color in range(self.n):
                            if other_color == color:
                                continue
                            
                            if nr in color_rows[other_color] and nc in color_cols[other_color]:
                                row_conflict = True
                                break
                        
                        if not row_conflict:
                            colors[nr][nc] = color
                            uncolored.remove((nr, nc))
                            color_rows[color].add(nr)
                            color_cols[color].add(nc)
                            progress = True
                            break
                
                if progress:
                    break
            
            if not progress and uncolored:
                cell = random.choice(list(uncolored))
                
                adjacent_colors = set()
                for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                    nr, nc = cell[0] + dr, cell[1] + dc
                    if 0 <= nr < self.n and 0 <= nc < self.n and colors[nr][nc] >= 0:
                        adjacent_colors.add(colors[nr][nc])
                
                if adjacent_colors:
                    color = random.choice(list(adjacent_colors))
                    colors[cell[0]][cell[1]] = color
                    uncolored.remove(cell)
                    color_rows[color].add(cell[0])
                    color_cols[color].add(cell[1])
        
        if uncolored:
            return None
        
        if not self._check_color_connectivity(colors):
            return None
        
        return colors

    def _generate_colors_with_constraints(self, cows: List[Tuple[int, int]]) -> Optional[List[List[int]]]:
        colors = [[-1 for _ in range(self.n)] for _ in range(self.n)]
        
        row_color = {}
        col_color = {}
        
        for i, (r, c) in enumerate(cows):
            colors[r][c] = i
            row_color[r] = i
            col_color[c] = i
        
        uncolored = {(r, c) for r in range(self.n) for c in range(self.n) if colors[r][c] == -1}
        
        for _ in range(self.n * self.n * 3):
            if not uncolored:
                break
            
            colored = [(r, c) for r in range(self.n) for c in range(self.n) if colors[r][c] >= 0]
            random.shuffle(colored)
            
            progress = False
            for r, c in colored:
                color = colors[r][c]
                
                neighbors = [(r+dr, c+dc) for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)] 
                             if 0 <= r+dr < self.n and 0 <= c+dc < self.n]
                random.shuffle(neighbors)
                
                for nr, nc in neighbors:
                    if colors[nr][nc] == -1:
                        colors[nr][nc] = color
                        uncolored.remove((nr, nc))
                        progress = True
                        break
                
                if progress:
                    break
        
        if uncolored:
            for r in range(self.n):
                for c in range(self.n):
                    if colors[r][c] == -1:
                        if r in row_color:
                            colors[r][c] = row_color[r]
                        elif c in col_color:
                            colors[r][c] = col_color[c]
                        else:
                            colors[r][c] = 0
        
        if not self._check_color_connectivity(colors):
            return None
        
        return colors

    def _check_color_connectivity(self, colors: List[List[int]]) -> bool:
        color_cells: Dict[int, List[Tuple[int, int]]] = {}
        for r in range(self.n):
            for c in range(self.n):
                color = colors[r][c]
                if color not in color_cells:
                    color_cells[color] = []
                color_cells[color].append((r, c))
        
        for color, cells in color_cells.items():
            if not cells:
                return False
            
            visited = set()
            queue = [cells[0]]
            visited.add(cells[0])
            
            while queue:
                r, c = queue.pop(0)
                for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.n and 0 <= nc < self.n:
                        if colors[nr][nc] == color and (nr, nc) not in visited:
                            visited.add((nr, nc))
                            queue.append((nr, nc))
            
            if len(visited) != len(cells):
                return False
        
        return True

    def _has_unique_solution(self, cows: List[Tuple[int, int]], colors: List[List[int]]) -> bool:
        solver = FastSolver(self.n, colors)
        solutions = solver.find_all_solutions(max_solutions=2)
        return len(solutions) == 1 and solutions[0] == set(cows)

    def _has_unique_solution_fast(self, cows: List[Tuple[int, int]], colors: List[List[int]]) -> bool:
        solver = FastSolver(self.n, colors)
        solutions = solver.find_all_solutions(max_solutions=2)
        return len(solutions) == 1 and solutions[0] == set(cows)

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


class FastSolver:
    def __init__(self, n: int, colors: List[List[int]]):
        self.n = n
        self.colors = colors
        self.color_cells: Dict[int, List[Tuple[int, int]]] = {}
        
        for r in range(n):
            for c in range(n):
                color = colors[r][c]
                if color not in self.color_cells:
                    self.color_cells[color] = []
                self.color_cells[color].append((r, c))
        
        self.colors_list = sorted(self.color_cells.keys())

    def find_all_solutions(self, max_solutions: int = 2) -> List[Set[Tuple[int, int]]]:
        solutions: List[Set[Tuple[int, int]]] = []
        
        color_order = sorted(self.colors_list, key=lambda c: len(self.color_cells[c]))
        
        self._backtrack(0, color_order, set(), set(), set(), solutions, max_solutions)
        
        return solutions

    def _backtrack(self, color_idx: int, color_order: List[int], 
                   used_rows: Set[int], used_cols: Set[int],
                   placed: Set[Tuple[int, int]], solutions: List[Set[Tuple[int, int]]],
                   max_solutions: int) -> bool:
        if len(solutions) >= max_solutions:
            return True
        
        if color_idx == len(color_order):
            solutions.append(placed.copy())
            return len(solutions) >= max_solutions
        
        color = color_order[color_idx]
        cells = self.color_cells[color]
        
        for r, c in cells:
            if r in used_rows or c in used_cols:
                continue
            
            conflict = False
            for pr, pc in placed:
                if abs(pr - r) <= 1 and abs(pc - c) <= 1:
                    conflict = True
                    break
            
            if conflict:
                continue
            
            placed.add((r, c))
            used_rows.add(r)
            used_cols.add(c)
            
            if self._backtrack(color_idx + 1, color_order, used_rows, used_cols, placed, solutions, max_solutions):
                return True
            
            placed.remove((r, c))
            used_rows.remove(r)
            used_cols.remove(c)
        
        return False
