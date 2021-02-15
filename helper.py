# https://www.geeksforgeeks.org/inplace-rotate-square-matrix-by-90-degrees/
def rotateMatrix(mat):
    N = len(mat)
    # Consider all squares one by one
    for x in range(0, int(N / 2)):

        # Consider elements in group
        # of 4 in current square
        for y in range(x, N - x - 1):
            # store current cell in temp variable
            temp = mat[x][y]

            # move values from right to top
            mat[x][y] = mat[y][N - 1 - x]

            # move values from bottom to right
            mat[y][N - 1 - x] = mat[N - 1 - x][N - 1 - y]

            # move values from left to bottom
            mat[N - 1 - x][N - 1 - y] = mat[N - 1 - y][x]

            # assign temp to left
            mat[N - 1 - y][x] = temp
