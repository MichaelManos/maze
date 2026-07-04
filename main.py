from __future__ import annotations

import random
import time
from tkinter import BOTH, Canvas, Tk

ANIMATE_TIME = 0.05
BLANK_COLOR = "#F0F0F0"


class Window:
    def __init__(self, width: int, height: int) -> None:
        self.root = Tk()
        self.root.title = "New Window"
        self.canvas = Canvas(width=width, height=height)
        self.canvas.pack()
        self.running = False
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def redraw(self) -> None:
        self.root.update_idletasks()
        self.root.update()

    def wait_for_close(self) -> None:
        self.running = True
        while self.running:
            self.redraw()

    def close(self) -> None:
        self.running = False

    def draw_line(self, line: Line, fill_color: str) -> None:
        line.draw(self.canvas, fill_color)


class Point:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y


class Line:
    def __init__(self, start: Point, end: Point) -> None:
        self.start = start
        self.end = end

    def draw(self, canvas: Canvas, fill_color: str) -> None:
        canvas.create_line(
            self.start.x,
            self.start.y,
            self.end.x,
            self.end.y,
            fill=fill_color,
            width=2,
        )


class Cell:
    def __init__(
        self,
        window: Window | None = None,
        has_left_wall: bool = True,
        has_right_wall: bool = True,
        has_top_wall: bool = True,
        has_bottom_wall: bool = True,
    ) -> None:
        self.has_left_wall = has_left_wall
        self.has_right_wall = has_right_wall
        self.has_top_wall = has_top_wall
        self.has_bottom_wall = has_bottom_wall

        self.__x1 = -1.0
        self.__x2 = -1.0
        self.__y1 = -1.0
        self.__y2 = -1.0
        self.__win = window

        self.visited = False

    def draw(self, top_left: Point, bottom_right: Point) -> None:
        self.__x1 = top_left.x
        self.__x2 = bottom_right.x
        self.__y1 = top_left.y
        self.__y2 = bottom_right.y
        if self.__win is not None:
            self.__win.draw_line(
                Line(
                    Point(self.__x1, self.__y1),
                    Point(self.__x1, self.__y2),
                ),
                "purple" if self.has_left_wall else BLANK_COLOR,
            )
            self.__win.draw_line(
                Line(
                    Point(self.__x2, self.__y1),
                    Point(self.__x2, self.__y2),
                ),
                "purple" if self.has_right_wall else BLANK_COLOR,
            )
            self.__win.draw_line(
                Line(
                    Point(self.__x1, self.__y1),
                    Point(self.__x2, self.__y1),
                ),
                "purple" if self.has_top_wall else BLANK_COLOR,
            )
            self.__win.draw_line(
                Line(
                    Point(self.__x1, self.__y2),
                    Point(self.__x2, self.__y2),
                ),
                "purple" if self.has_bottom_wall else BLANK_COLOR,
            )

    def center(self) -> Point:
        x = (self.__x1 + self.__x2) / 2
        y = (self.__y1 + self.__y2) / 2
        return Point(x, y)

    def draw_move(self, to_cell: Cell, undo: bool = False) -> None:
        line = Line(self.center(), to_cell.center())
        fill_color = BLANK_COLOR if undo else "red"
        if self.__win is not None:
            self.__win.draw_line(line, fill_color)


class Maze:
    def __init__(
        self,
        x1: int,
        y1: int,
        num_rows: int,
        num_cols: int,
        cell_size_x: float,
        cell_size_y: float,
        win: Window | None = None,
        seed: int | None = None,
    ) -> None:
        self.x1 = x1
        self.y1 = y1
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.cell_size_x = cell_size_x
        self.cell_size_y = cell_size_y
        self.win = win

        if seed is not None:
            seed = random.seed(seed)

        self.__cells = []
        self.__create_cells()
        self.__break_entrance_and_exit()
        self.__break_walls_r(0, 0)
        self.__reset_cells_visited()

    def __create_cells(self):
        # Create
        for _ in range(self.num_cols):
            row_list = []
            for _ in range(self.num_rows):
                row_list.append(Cell(self.win))
            self.__cells.append(row_list)

        # Draw
        for x in range(self.num_rows):
            for y in range(self.num_cols):
                self._draw_cell(y, x)

    def _draw_cell(self, i: int, j: int) -> None:
        cell_x = self.x1 + i * self.cell_size_x
        cell_y = self.y1 + j * self.cell_size_y
        top_left = Point(cell_x, cell_y)
        bottom_right = Point(
            cell_x + self.cell_size_x, cell_y + self.cell_size_y
        )
        self.__cells[i][j].draw(top_left, bottom_right)
        self.__animate()

    def __animate(self) -> None:
        if self.win is not None:
            self.win.redraw()
            time.sleep(ANIMATE_TIME)

    def __break_entrance_and_exit(self) -> None:
        self.__cells[0][0].has_top_wall = False
        self._draw_cell(0, 0)
        self.__cells[self.num_cols - 1][
            self.num_rows - 1
        ].has_bottom_wall = False
        self._draw_cell(self.num_cols - 1, self.num_rows - 1)

    def __break_walls_r(self, i, j) -> None:
        """i is column number, j is row number (0-indexed)"""
        self.__cells[i][j].visited = True
        while True:
            available_moves = []
            if i > 0:
                if self.__cells[i - 1][j].visited == False:
                    available_moves.append("left")
            if i < self.num_cols - 1:
                if self.__cells[i + 1][j].visited == False:
                    available_moves.append("right")
            if j > 0:
                if self.__cells[i][j - 1].visited == False:
                    available_moves.append("up")
            if j < self.num_rows - 1:
                if self.__cells[i][j + 1].visited == False:
                    available_moves.append("down")
            if len(available_moves) == 0:
                self._draw_cell(i, j)
                return
            next_move = random.choice(available_moves)
            if next_move == "left":
                self.__cells[i][j].has_left_wall = False
                self.__cells[i - 1][j].has_right_wall = False
                self.__break_walls_r(i - 1, j)
            elif next_move == "right":
                self.__cells[i][j].has_right_wall = False
                self.__cells[i + 1][j].has_left_wall = False
                self.__break_walls_r(i + 1, j)
            elif next_move == "up":
                self.__cells[i][j].has_top_wall = False
                self.__cells[i][j - 1].has_bottom_wall = False
                self.__break_walls_r(i, j - 1)
            elif next_move == "down":
                self.__cells[i][j].has_bottom_wall = False
                self.__cells[i][j + 1].has_top_wall = False
                self.__break_walls_r(i, j + 1)

    def __reset_cells_visited(self):
        for row in self.__cells:
            for cell in row:
                cell.visited = False

    def solve(self):
        return self._solve_r(0, 0)

    def _solve_r(self, i, j):
        self.__animate()
        current_cell: Cell = self.__cells[i][j]
        current_cell.visited = True
        if i == self.num_cols - 1 and j == self.num_rows - 1:
            return True
        # left
        if i > 0 and not current_cell.has_left_wall:
            candidate_cell = self.__cells[i - 1][j]
            if not candidate_cell.visited:
                current_cell.draw_move(candidate_cell)
                if self._solve_r(i - 1, j):
                    return True
                current_cell.draw_move(candidate_cell, undo=True)
        # right
        if i < self.num_cols - 1 and not current_cell.has_right_wall:
            candidate_cell = self.__cells[i + 1][j]
            if not candidate_cell.visited:
                current_cell.draw_move(candidate_cell)
                if self._solve_r(i + 1, j):
                    return True
                current_cell.draw_move(candidate_cell, undo=True)
        # north
        if j > 0 and not current_cell.has_top_wall:
            candidate_cell = self.__cells[i][j - 1]
            if not candidate_cell.visited:
                current_cell.draw_move(candidate_cell)
                if self._solve_r(i, j - 1):
                    return True
                current_cell.draw_move(candidate_cell, undo=True)
        # south
        if j < self.num_rows - 1 and not current_cell.has_bottom_wall:
            candidate_cell = self.__cells[i][j + 1]
            if not candidate_cell.visited:
                current_cell.draw_move(candidate_cell)
                if self._solve_r(i, j + 1):
                    return True
                current_cell.draw_move(candidate_cell, undo=True)
        return False


def main():
    win = Window(810, 610)
    maze = Maze(5, 5, 12, 16, 50, 50, win)
    maze.solve()
    win.wait_for_close()


if __name__ == "__main__":
    main()
