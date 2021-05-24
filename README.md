# Play online chess with real chess board
Program that enables you to play online chess using real chess board.  Using computer vision it will detect the moves you make on chess board. After that, if it's your turn to move in the online game, it will make the necessary clicks to make the move.

## Setup

1. Turn off all the animations and extra features to keep chess board of online game as simple as possible.

2. Take screenshots of chess board of online game at starting position, one for when you play white and one for when you play black and save them as "white.JPG" and "black.JPG" similar to the images included in the source code.

3. Enable auto promotion to queen from settings of online game.

4. Place your webcam near to your chessboard so that all of the squares and pieces can be clearly seen by it.

5. Remove all pieces from your chess board.

6. Run "board_calibration.py".

7. Check that corners of your chess board are correctly detected by "board_calibration.py" and press key "q" to save detected chess board corners. You don't need to manually select chess board corners, it should be automatically detected by the program. The square covered by points (0,0), (0,1),(1,0) and (1,1) should be a8. You can rotate the image by pressing key "r" to adjust that. Example chess board detection result:

   ![](https://github.com/karayaman/Play-online-chess-with-real-chess-board/blob/main/chessboard_detection_result.jpg?raw=true)

8. Note that "constants.bin" file is created or modified.

## Usage

1. Place pieces of chess board to their starting position.
2. Start the online game.
3. Run "main.py".
4. Switch to the online game so that program detects chess board of online game. You have 5 seconds to do this step.
5.  Wait until program says "game started".
6. Make your move if it's your turn , otherwise make opponent's move.
8. Notice that program actually makes your move on the internet game if it's your turn. Otherwise, wait until program says starting and ending squares of opponent's move. 
9. Go to step 6.

## GUI

You can run "gui.py" to open the GUI. You can use it to do the steps in Setup and Usage sections and customize how you use the software. You can click "Start Game" button instead of running "main.py" and "Board Calibration" button instead of running "board_calibration.py".

![](https://github.com/karayaman/Play-online-chess-with-real-chess-board/blob/main/gui.JPG?raw=true)

## Video

In this section you can find video content related to the software.

[Game against Stockfish 5 2000 ELO](https://youtu.be/6KV4kHBKh3w)

[Test game on chess.com](https://youtu.be/Z3-hE0JbJf0)

## Frequently Asked Questions

### What is the program doing? How it works? 

It tracks your chess board via webcam. You should place it on top of your chess board. Make sure there
is enough light in the environment and all squares are clearly visible. When you make a move on your chess board, it understands the move you made and transfers it to chess GUI by simulating mouse clicks(It clicks starting and ending squares of your move). This way, using your chess board, you can play chess in any chess program either websites like lichess.org, chess.com or desktop programs like Fritz, Chessmaster etc.

### Placing webcam on top of the chess board sounds difficult. Can I put my laptop aside with the webcam in the laptop display?

Yes, you can do that with a small chess board. However placing webcam on top of the chess board is recommended. Personally, while using the program I am putting my laptop aside and it gives out moves via chess gui and show clocks. Instead of using laptop's webcam, I disable it
and use my old android phone's camera as webcam using an app called DroidCam. I place my phone
somewhere high enough(bookshelf for instance) so that all of the squares and pieces can be clearly seen by it.

### How well it works?

Using this software I am able to make up to 100 moves in 15+10 rapid online game without getting any errors.

### If I use the two exe-files (and not the py-files), where do I have to store the new white.JPG and black.JPG files?

If you use the two exe-files( "main.exe" and "board_calibration.exe") you should create a folder for them and put the two exe-files, "white.JPG" and "black.JPG" files into that folder.

### I am getting error message "Move registration failed. Please redo your move." What is the problem?

Program asked you to redo your move because it understood that you made a move. However, it failed to figure out which move you made. This can happen if your board calibration is incorrect or color of your pieces are very similar to color of your squares. If latter is the case you will get this error message when playing white piece to light square or black piece to dark square. 

### Why it takes forever to detect corners of the chess board?

It should detect corners of the chess board almost immediately. Please do not spend any time waiting for it to detect corners of the chess board. If it can't detect corners of the chess board almost immediately, this means that it can't see your chess board well from that position/angle. Placing your webcam somewhere a bit higher or lower might solve the issue.

## Required libraries

- opencv
- python-chess
- pyautogui
- mss
- numpy
- pyttsx3
- scikit-image