import cv2
import numpy as np

# Görüntüyü yeniden boyutlandırma
def resize_image(image, width=736, height=441):
    return cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)

# Görüntü yolu
image_path = 'pcb_image.jpg'
image = cv2.imread(image_path)

if image is None:
    print("Error: Image not found.")
    exit()

# Görüntüyü yeniden boyutlandır
image = resize_image(image)

# Gri tonlama
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Sabit değerler
threshold1 = 42
threshold2 = 173
blur_level = 20

if blur_level % 2 == 0:
    blur_level += 1  # Blur seviyesini tek sayıya çıkar

# Görüntü iyileştirme
enhanced = cv2.convertScaleAbs(gray, alpha=1.5, beta=30)
blurred = cv2.GaussianBlur(enhanced, (blur_level, blur_level), 0)

# Kenar tespiti
edges = cv2.Canny(blurred, threshold1, threshold2)

# Kontur tespiti
contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# En büyük konturu al ve döndürülebilir dikdörtgeni bul
if contours:
    # En büyük konturu seç
    largest_contour = max(contours, key=cv2.contourArea)

    # Döndürülebilir dikdörtgeni bul
    rect = cv2.minAreaRect(largest_contour)
    box = cv2.boxPoints(rect)
    box = np.int0(box)  # Köşe noktalarını tam sayıya çevir

    # Orijinal görüntü üzerine dikdörtgeni çiz
    image_with_box = image.copy()
    cv2.drawContours(image_with_box, [box], 0, (0, 255, 0), 2)

    # Dikdörtgenin içindeki alanı kırp
    x, y, w, h = cv2.boundingRect(box)
    cropped_image = image[y:y + h, x:x + w]

    # Kırpılmış görüntüyü sabit boyuta yeniden boyutlandır
    output_width = 736
    output_height = 441
    filled_image = resize_image(cropped_image, width=output_width, height=output_height)

    # Sonuçları göster
    cv2.imshow("Original Image with Box", image_with_box)
    cv2.imshow("Cropped Object", filled_image)
else:
    print("Nesne bulunamadı!")

# Kenar tespiti sonucunu göster
cv2.imshow("Edges", resize_image(edges))

cv2.waitKey(0)
cv2.destroyAllWindows()
