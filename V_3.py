import cv2
import time
import random
import threading
from playsound import playsound

soundplay = 0
correct_side = ''
display_image = ''
start_time = 0
game_over = False
game_start = False
status = 0
score = 0
rdtime = 0
delaycount = False

# Load the pre-trained Haar Cascade face detector
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def detect_faces(frame):
    global status, game_start, game_over
    height, width, _ = frame.shape
    frame = frame[400:height-200, :]

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    for (x, y, w, h) in faces:
        center = (x + w // 2, y + h // 2)
        print(type(center), center)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

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

def play_sound_in_thread(file_path):
    threading.Thread(target=playsound, args=(file_path,), daemon=True).start()

def play(h, w, f):  # Function to play the game
    global game_start, status, game_over, start_time, score, display_image, correct_side, rdtime, delaycount
    if start_time == 0:
        start_time = time.time()
        correct_side = random.choice(['left', 'right'])
        if correct_side == 'left':
            display_image = "<"
        else:
            display_image = ">"
        rdtime = random.randint(1, 2)
        print(rdtime)

    elapsed_time = time.time() - start_time
    cv2.putText(f, f'Time left : {max(0, rdtime - elapsed_time):.2f}', (w - 600, 150), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 5)
    cv2.putText(f, f'Move : {display_image}', (650, h-50), cv2.FONT_HERSHEY_SIMPLEX, 4, (random.randint(1,255), random.randint(1,255), random.randint(1,255)), 8)

    if elapsed_time > rdtime:
        game_start = False
        if (correct_side == 'left' and status == 1) or (correct_side == 'right' and status == 2):
            score += 1
            cv2.putText(f, f'Score +1', (500, 500), cv2.FONT_HERSHEY_SIMPLEX, 4, (0, 255, 0), 8)
            play_sound_in_thread('/Users/pathorn/python/lab8/assignment/sound/Ping sound effect.mp3')
        else:
            game_over = True
            play_sound_in_thread('/Users/pathorn/python/lab8/assignment/sound/Game Over sound effect.mp3')
        start_time = 0
        elapsed_time = 0
        delaycount = False
def delay():
    global delaycount, start_delay, soundplay
    if not delaycount and soundplay == 0:
        play_sound_in_thread('/Users/pathorn/python/lab8/assignment/sound/3 2 1 0 Countdown With Sound Effect  No Copyright  Ready To Use.mp3')
        soundplay = 1
    if time.time() - start_delay > 3:
        delaycount = True

def show_gameover(f, height):
    frame = f
    cv2.putText(frame, f'Score : {score}', (700, 300), cv2.FONT_HERSHEY_SIMPLEX, 4, (0, 0, 255), 8)
    cv2.putText(frame, f'GAME OVER', (200, height//2+200), cv2.FONT_HERSHEY_SIMPLEX, 9, (0, 0, 255), 8)
    cv2.putText(frame, f'PRESS R TO RESET', (550, height//2+400), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255), 8)
    return frame

def draw_frame(frame, width, height):
    cv2.line(frame, (width // 2, 200), (width // 2, height-150), (0, 0, 0), 9)
    cv2.line(frame, (0, 200), (width, 200), (0, 0, 0), 9)
    cv2.line(frame, (0, height - 150), (width, height - 150), (0, 0, 0), 9)
    cv2.putText(frame, f'Score : {score}', (width // 2 - 250, 150), cv2.FONT_HERSHEY_SIMPLEX, 4, (0, 0, 255), 8)

def main():
    global status, game_start, score, start_time, game_over, delaycount, start_delay, soundplay
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        frame = cv2.flip(frame, 1)
        if not ret:
            print("Cannot open camera.")
            break

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

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        height, width, _ = frame.shape

        if game_over:
            frame = show_gameover(gray, height)
        else:
            if game_start:
                if not delaycount:
                    delay()
                    cv2.putText(frame, f'{3-int(time.time() - start_delay)}', (width // 2, height // 2), cv2.FONT_HERSHEY_SIMPLEX, 4, (0, 0, 255), 8)
                else:
                    draw_frame(frame, width, height)
                    play(height, width, frame)
                    detect_faces(frame)
            else:
                soundplay = 0
                if score == 0:
                    cv2.putText(frame, f'PRESS A TO PLAY', (700, height-100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 8)
                else:
                    status = 0
                    cv2.putText(frame, f'Score : {score}', (700, 300), cv2.FONT_HERSHEY_SIMPLEX, 4, (0, 0, 255), 8)
                    cv2.putText(frame, f'Score +1', (900, 200), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 150), 8)
                    cv2.putText(frame, f'PRESS A TO CONTINUE', (600, height-100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 8)
        cv2.imshow("Detected Faces", frame)
    cap.release()
    cv2.destroyAllWindows()

# Start the game
main()
