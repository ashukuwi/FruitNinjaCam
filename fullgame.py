import pygame
import os
import random
import cv2
import mediapipe as mp
import pyautogui
import keyboard

pygame.init()
WIDTH, HEIGHT = 1000, 600
pygame.init()
akhilisbetterthanashvith = False
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fruit Ninja")
BG_COLOR = (46, 32, 25)
TEXT_COLOR = (255, 255, 255)
score = 0
FPS = 300
FRUIT_NUM = 5
bombs = []
STRAWBERRY = pygame.image.load(os.path.join("images", "strawberry.png"))
APPLE = pygame.image.load(os.path.join("images", "apple.png"))
BANANA = pygame.image.load(os.path.join("images", "banana.png"))
COCONUT = pygame.image.load(os.path.join("images", "coconut.png"))
PINEAPPLE = pygame.image.load(os.path.join("images", "pineapple.png"))
WATERMELON = pygame.image.load(os.path.join("images", "watermelon.png"))
EXPLOSION = pygame.image.load(os.path.join("images", "explosion.png"))
BOMB = pygame.image.load(os.path.join("images", "tnt.png"))
FRUIT_WIDTH, FRUIT_HEIGHT = 75, 75
BOMB_WIDTH, BOMB_HEIGHT = 150, 150
mp_hands = mp.solutions.hands.HandLandmark
width, height = pyautogui.size()
hands = mp.solutions.hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5,
                                 min_tracking_confidence=0.5)
cap = cv2.VideoCapture(0)
pyautogui.PAUSE = 0

STRAWBERRY, APPLE, BANANA, COCONUT, PINEAPPLE, WATERMELON, BOMB, EXPLOSION = list(
    map(lambda x: pygame.transform.scale(x, (FRUIT_WIDTH, FRUIT_HEIGHT)),
        [STRAWBERRY, APPLE, BANANA, COCONUT, PINEAPPLE, WATERMELON, BOMB, EXPLOSION]))
FRUIT_IMAGES = [STRAWBERRY, APPLE, BANANA, COCONUT, PINEAPPLE, WATERMELON, BOMB, EXPLOSION]

font = pygame.font.Font('freesansbold.ttf', 32)


# create a text surface object,
# on which text is drawn on it.

def extended(finger_tip, finger_mcp, wrist):
    x = finger_tip.y - wrist.y
    y = finger_mcp.y - wrist.y

    if x < 0:
        if x < y:
            return True
        else:
            return False
    else:
        if x > y:
            return True
        else:
            return False


class Fruit:
    def __init__(self, index):

        self.img = FRUIT_IMAGES[index]
        self.isBomb = self.img == BOMB
        self.isCut = False
        self.x = random.randint(0, WIDTH)
        self.horizontalSpeed = random.randint(225, 270)
        if self.isBomb:
            self.horizontalSpeed *= 2
        self.perm_x = self.x
        self.y = HEIGHT - FRUIT_HEIGHT
        self.height = random.randint(12, 22)
        self.rate = 1
        self.deathEffectCounter = FPS

    def update(self):
        if not self.isCut:
            if self.y < 1000:
                if self.rate > 0:
                    self.rate *= 0.96
                if self.rate < 0:
                    self.rate /= 0.96
                if 0 < self.rate < 0.01:
                    self.rate *= -1
                if self.perm_x > WIDTH / 2:
                    self.x -= self.perm_x / self.horizontalSpeed
                else:
                    self.x += (WIDTH - self.perm_x) / self.horizontalSpeed
                self.y -= self.rate * self.height
        else:
            self.img = FRUIT_IMAGES[-1]


banana = Fruit(2)
apple = Fruit(1)
strawberry = Fruit(0)
fruitObjects = [Fruit(random.randint(0, 5)) for i in range(random.randint(5, 12))]
for i in range(2, 9):
    if random.choice(range(2, i + 1)) == 2:
        fruitObjects.append(Fruit(-2))


def draw():
    window.fill(BG_COLOR)
    text = font.render('{}'.format(score), True, TEXT_COLOR)

    # create a rectangular object for the
    # text surface object
    textRect = text.get_rect()

    # set the center of the rectangular object.
    textRect.center = (WIDTH / 2, 50)
    window.blit(text, textRect)
    for fruit in fruitObjects:
        if not fruit.isCut:
            window.blit(fruit.img, (fruit.x, fruit.y))
        else:
            fruit.deathEffectCounter -= 1
            if fruit.deathEffectCounter >= 0:
                window.blit(fruit.img, (fruit.x, fruit.y))
            else:
                fruit.x = WIDTH
                fruit.y = HEIGHT
    pygame.display.update()


clock = pygame.time.Clock()
run = True
while run:
    clock.tick(FPS)
    # Computer Vision Code
    ret, frame = cap.read()

    if not ret:
        break

    frame = cv2.flip(frame, 1)

    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(image_rgb)

    if results.multi_hand_landmarks:
        # Get landmarks of the first hand (assuming one hand is visible)
        hand_landmarks = results.multi_hand_landmarks[0]

        index_finger_tip = hand_landmarks.landmark[mp_hands.INDEX_FINGER_TIP]
        index_finger_mcp = hand_landmarks.landmark[mp_hands.INDEX_FINGER_MCP]
        middle_finger_tip = hand_landmarks.landmark[mp_hands.MIDDLE_FINGER_TIP]
        middle_finger_mcp = hand_landmarks.landmark[mp_hands.MIDDLE_FINGER_MCP]
        wrist = hand_landmarks.landmark[mp_hands.WRIST]

        if extended(index_finger_tip, index_finger_mcp, wrist) and extended(middle_finger_tip, middle_finger_mcp,
                                                                            wrist):
            pyautogui.mouseDown(button="left")
        else:
            pyautogui.mouseUp(button="left")

        cx, cy = int(index_finger_tip.x * width), int(index_finger_tip.y * height)

        # Move cursor to index finger coordinates
        pyautogui.moveTo(cx, cy, duration=0)


    for event in pygame.event.get():
        if event == pygame.QUIT:
            run = False
        for fruit in fruitObjects:
            currentMousePos = pygame.mouse.get_pos()
            currentMouseClicked = pygame.mouse.get_pressed()
            if fruit.x > WIDTH or fruit.y > HEIGHT:
                fruit.isCut = True

            if any(currentMouseClicked) and (
                    (fruit.x + FRUIT_WIDTH) >= currentMousePos[0] >= fruit.x and (fruit.y + FRUIT_HEIGHT) >=
                    currentMousePos[1] >= fruit.y):
                if not fruit.isCut and not fruit.isBomb:
                    score += 1
                elif fruit.isBomb:
                    score = 0
                fruit.isCut = True
        if not any([not fruit.isCut for fruit in fruitObjects]):
            fruitObjects = [Fruit(random.randint(0, 5)) for i in range(random.randint(5, 12))]
            for i in range(2, 9):
                if random.choice(range(2, i + 1)) == 2:
                    fruitObjects.append(Fruit(-2))
    draw()
    for fruit in fruitObjects:
        fruit.update()

    if keyboard.is_pressed("q"):
        break

pygame.quit()