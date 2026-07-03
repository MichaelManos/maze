import unittest

from main import Maze


class Tests(unittest.TestCase):
    def test_maze_create_cells(self):
        num_cols = 12
        num_rows = 10
        m1 = Maze(0, 0, num_rows, num_cols, 10, 10)
        self.assertEqual(
            len(m1._Maze__cells),
            num_cols,
        )
        self.assertEqual(
            len(m1._Maze__cells[0]),
            num_rows,
        )

    def test_break_entrance_exit(self):
        num_cols = 12
        num_rows = 10
        m1 = Maze(0, 0, num_rows, num_cols, 10, 10)
        m1._Maze__break_entrance_and_exit()

        top_left_cell = m1._Maze__cells[0][0]
        self.assertEqual(
            top_left_cell.has_top_wall,
            False,
        )

        bottom_right_cell = m1._Maze__cells[11][9]
        self.assertEqual(
            bottom_right_cell.has_bottom_wall,
            False,
        )

    def test_maze_reset_cells_visited(self):
        num_cols = 12
        num_rows = 10
        m1 = Maze(0, 0, num_rows, num_cols, 10, 10)
        m1._Maze__cells[6][3].visited = True
        m1._Maze__reset_cells_visited()
        self.assertEqual(
            m1._Maze__cells[6][3].visited,
            False,
        )


if __name__ == "__main__":
    unittest.main()
