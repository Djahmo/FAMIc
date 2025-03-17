import threading
import pygetwindow as gw
import pyautogui
import cv2
import numpy as np
from PIL import Image
from overlay import Overlay
from commons import matchWithColor, matchWithColorM
import win32gui # type: ignore
import time
import mss

windowName = "Farmer Against Potatoes Idle"

def getImg():
     with mss.mss() as sct:
        monitor = {
            "top": clientY,
            "left": clientX,
            "width": clientWidth,
            "height": clientHeight
        }

        screenshot = sct.grab(monitor)
        img = np.array(screenshot)
        img = img[:, :, :3]
        img = img[:, :, ::-1]
        return img

while True:
    gameWindow = gw.getWindowsWithTitle(windowName)
    if gameWindow:
        gameWindow = gameWindow[0]
        print(f"Fenêtre trouvée : {gameWindow.title}")

        # Trouver les limites réelles en détectant les bords non noirs
        def getClientArea(windowName):
            hwnd = win32gui.FindWindow(None, windowName)
            rect = win32gui.GetClientRect(hwnd)
            x, y = win32gui.ClientToScreen(hwnd, (rect[0], rect[1]))  # Convertir en coordonnées écran
            width, height = rect[2] - rect[0], rect[3] - rect[1]

            return x, y, width, height
        
        clientX, clientY, clientWidth, clientHeight = getClientArea(windowName)

        img = getImg()

        def findEdges(rgbImg):
            topEdge = next((y for y in range(clientHeight) if not matchWithColor(rgbImg[y, clientWidth // 2], "#000000")), clientHeight)
            leftEdge = next((x for x in range(clientWidth) if not matchWithColor(rgbImg[clientHeight // 2, x], "#000000")), clientWidth)
            return topEdge, leftEdge

        print(f"Avant ajustement : x={clientX}, y={clientY}, width={clientWidth}, height={clientHeight}")

        topEdge, leftEdge = findEdges(img)

        print(f"Bords détectés : top={topEdge}, left={leftEdge}")

        clientX += leftEdge
        clientY += topEdge
        clientWidth -= leftEdge*2
        clientHeight -= topEdge*2

        print(f"Zone client du jeu : x={clientX}, y={clientY}, width={clientWidth}, height={clientHeight}")

        break
    else:
        print("Fenêtre non trouvée, nouvelle tentative dans 5 secondes...")
        time.sleep(5)



def backgroundTask(overlay):
    """Thread qui exécute des actions en parallèle de l'overlay"""
    while True:

        img = getImg()
        #WHACK
        px, py = overlay.getPixelPosition(27, 1, local=True)
        if matchWithColorM(img, px, py, "#d4d010"):
            overlay.clickOnCell(27, 1)
            overlay.clickOnCell(13, 21)
            time.sleep(3)
            tab = [
                [7, 6], [10, 6], [13, 6], [16, 6], [19, 6], 
                [7, 11], [10, 11], [13, 11], [16, 11], [19, 11],
                [7, 16], [10, 16], [13, 16], [16, 16], [19, 16]
            ]
            pixel_positions = [(overlay.getPixelPosition(x, y, local=True), x, y) for x, y in tab]

            startTime = time.time()

            while time.time() - startTime < 60:
                img = getImg()
                for (px, py), x, y in pixel_positions:
                    color_match = matchWithColorM(img, px, py, "#d1964a") or matchWithColorM(img, px, py, "#fdbf17")
                    if color_match:
                        overlay.clickOnCell(x, y)
                        time.sleep(0.02)
                        
            overlay.clickOnCell(6, 21)
            time.sleep(1)

        overlay.clickOnCell(1, 21)

        #RESTART
        img = getImg()

        px, py = overlay.getPixelPosition(7, 11, local = True)
        if matchWithColorM(img, px, py, "#101110"):
            overlay.clickOnCell(7, 11)
            time.sleep(2)
            
        time.sleep(30)  # Pause pour éviter un spam trop rapide

# Initialisation de l'overlay
overlay = Overlay(clientX, clientY, clientWidth, clientHeight)
overlay.drawGrid(0)

# Lancement du thread en arrière-plan
thread = threading.Thread(target=backgroundTask, args=(overlay,), daemon=True)
thread.start()

overlay.run()