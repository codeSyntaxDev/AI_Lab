def print_solution(board, n):
    for row in board:
        print(" ".join("Q" if col else "." for col in row))
    print("\n")

def is_safe(board, row, col, n):
    # Check column
    for i in range(row):
        if board[i][col]:
            return False
    
    # Check upper-left diagonal
    for i, j in zip(range(row, -1, -1), range(col, -1, -1)):
        if board[i][j]:
            return False
    
    # Check upper-right diagonal
    for i, j in zip(range(row, -1, -1), range(col, n)):
        if board[i][j]:
            return False
    
    return True

def solve_n_queens_util(board, row, n):
    if row == n:
        print_solution(board, n)
        return True
    
    res = False
    for col in range(n):
        if is_safe(board, row, col, n):
            board[row][col] = 1
            res = solve_n_queens_util(board, row + 1, n) or res
            board[row][col] = 0  # Backtrack
    
    return res

def solve_n_queens(n):
    board = [[0] * n for _ in range(n)]
    if not solve_n_queens_util(board, 0, n):
        print("No solution exists")
    
if __name__ == "__main__":
    n = int(input("Enter the value of N for the N-Queens problem: "))
    solve_n_queens(n)