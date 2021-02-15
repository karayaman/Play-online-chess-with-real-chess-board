# Play online chess with real chess board
Program that enables you to play online chess using real chess board.  Using computer vision it will detect the moves you make on chess board. After that, if it's your turn to move in the internet game, it will make the necessary clicks to make the move.

## Setup

1. Turn off all the animations and extra features to keep chess board of internet game as simple as possible.
2.  Take screenshots of chess board of internet game at starting position, one for when you play white and one for when you play black and save them as "white.JPG" and "black.JPG" similar to the images included in the source code.
3. Place your webcam near to your chessboard so that all of the squares and pieces can be clearly seen by it.
4. Remove all pieces from your chess board.
5. Run "board_calibration.py".
6. Check that corners of your chess board are correctly detected by "board_calibration.py" and press key "q" to save detected chess board corners.
7. Note that "constants.bin" file is created or modified.

## Usage

1. Place pieces of chess board to their starting position.
2. Start the internet game.
3. Run "main.py".
4. Switch to the internet game so that program detects chess board of internet game. You have 5 seconds to do this step.
5.  Hear that program says "game started".
6. Make your move if it's your turn , otherwise make opponent's move. When you start to make a move program will say "motion" to let you know that it knows that you are about to make a move.
7. Hear that program says starting and ending squares of your move.
8. Notice that program actually makes your move on the internet game if it's your turn.
9. Go to step 6.

## Required libraries
- skimage
- opencv
- python-chess
- pyautogui
- mss
- numpy
- pyttsx3