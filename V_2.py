import cv2
import numpy as np
import time
import random
correct_side = ''
display_image = ''
start_time = 0
game_over = False
game_start = False
status = 0
score = 0
rdtime = 0
delaycount = False
def detect_circles(frame): #ฟังก์ชั่นตรวจจับวัตถุวงกลม
    global status, game_start, game_over
    height, width, _ = frame.shape
    frame = frame[400:height-200, :]

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (9, 9), 2)

    circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=1, minDist=150,
                                param1=100, param2=50, minRadius=30, maxRadius=250)

    if circles is not None:
        circles = np.uint16(np.around(circles))
        for circle in circles[0, :]:
            center = (circle[0], circle[1])
            radius = circle[2]
            cv2.circle(frame, center, radius, (0, 255, 0), 2)  # Draw circle
            cv2.circle(frame, center, 2, (0, 0, 255), 3)  # Draw center point

            # Determine if the circle is on the left or right
            if center[0] < width // 2:
                status = 1  # Left
            else:
                status = 2  # Right

    if status == 1:
        cv2.putText(frame, 'Left', (300, 300), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 10)
    elif status == 2:
        cv2.putText(frame, 'Right', (width - 600, 300), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 10)
    else:
        cv2.putText(frame, 'Not found', (width // 2 - 50, 400), cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 0, 255), 10)

def play(h, w, f): #ฟังก์ชั่นเล่นเกม
    global game_start, status, game_over, start_time, score, display_image, correct_side, rdtime, delaycount
    # Only start timing when the game starts
    if start_time == 0:
        start_time = time.time()
        correct_side = random.choice(['left', 'right'])
        if correct_side == 'left':
            display_image = "<"
        else:
            display_image = ">"
        rdtime = random.randint(1,2)
        print(rdtime)

    elapsed_time = time.time() - start_time
    cv2.putText(f, f'Time left : {max(0, rdtime - elapsed_time):.2f}', (w - 600, 150), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 5)
    cv2.putText(f, f'Move : {display_image}', (650, h-50), cv2.FONT_HERSHEY_SIMPLEX, 4, (0, 255, 0), 8)


    if elapsed_time > rdtime:
        game_start = False
        if (correct_side == 'left' and status == 1) or (correct_side == 'right' and status == 2):
            score += 1
        else:
            game_over = True
        start_time = 0
        elapsed_time = 0
        delaycount = False

def delay(): #ฟังก์ชั่นดีเลย์ก่อนเริ่มเกม
    global delaycount ,start_delay
    if time.time() - start_delay > 3:
        delaycount = True

def main(): #ฟังก์ชั่นหลัก
    global status, game_start, score, start_time, game_over, delaycount, start_delay
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        frame = cv2.flip(frame,1)
        if not ret:
            print("Cannot open camera.")
            break
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        height, width, _ = frame.shape
        if game_over:
            frame = gray
            cv2.putText(frame, f'Score : {score}', (700, 300), cv2.FONT_HERSHEY_SIMPLEX, 4, (0, 0, 255), 8)
            cv2.putText(frame, f'GAME OVER', (200, height//2+200), cv2.FONT_HERSHEY_SIMPLEX, 9, (0, 0, 255), 8)
            cv2.putText(frame, f'PRESS R TO RESET', (550, height//2+400), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255), 8)
        else:
            if game_start:
                if not delaycount:
                    delay()
                    cv2.putText(frame, f'{3-int(time.time() - start_delay)}', (width // 2 ,height // 2), cv2.FONT_HERSHEY_SIMPLEX, 4, (0, 0, 255), 8)
                else:
                    cv2.line(frame, (width // 2, 200), (width // 2, height-150), (0, 0, 0), 9)  # Draw vertical line
                    cv2.line(frame, (0, 200), (width, 200), (0, 0, 0), 9)  # Horizontal line at 200px
                    cv2.line(frame, (0, height - 150), (width, height - 150), (0, 0, 0), 9)  # Horizontal line at height - 150px
                    cv2.putText(frame, f'Score : {score}', (width // 2 - 250, 150), cv2.FONT_HERSHEY_SIMPLEX, 4, (0, 0, 255), 8)
                    play(height, width, frame)
                    detect_circles(frame)  # Call circle detection here
            else:
                if score == 0:
                    cv2.putText(frame, f'PRESS A TO PLAY', (700, height-100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 8)
                else:
                    cv2.putText(frame, f'PRESS A TO CONTINUE', (600, height-100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 8)



        cv2.imshow("Detected Circles", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('a'):
            if game_over:
                continue
            game_start = not game_start
            start_delay = time.time()
            print('Game started:', game_start)

        if cv2.waitKey(1) & 0xFF == ord('r'):
            game_over = False
            score = 0

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Start the game
main()
