import cv2
import cvzone
import numpy as np
from fastapi import FastAPI, UploadFile
import requests


app = FastAPI()

@app.get('/')
def root():
    return {'Message': 'Tongue Detect Server'}

@app.post('/proses')
async def proccess(file: UploadFile):
    contens = await file.read()
    nparr = np.fromstring(contens, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    imgFront = cv2.imread("OverLay.png", cv2.IMREAD_UNCHANGED)

    # Resize the overlay image to match the frame size
    hf, wf, _ = img.shape

    ratio = imgFront.shape[1]/imgFront.shape[0]

    print(imgFront.shape)


    new_width = int(ratio * hf)
    x_diff = wf - new_width
    x_offset = x_diff // 2


    scale = new_width / imgFront.shape[1]

    x1, y1 = (int((scale * 550) + x_offset), int(scale * 506))
    x2, y2 = (int((scale * 1060) + x_offset), int(scale * 936))

    imgFront = cv2.resize(imgFront, (new_width, hf))

    imgResult = cvzone.overlayPNG(img, imgFront, pos=[x_offset, 0])

    imgResult = imgResult[y1:y2, x1:x2]

    imgResult = cv2.resize(imgResult,dsize=None, fx = 0.5, fy=0.5)

    red_mask, white_mask, tongue_mask = detect_full_tongue(imgResult)

    # Hitung luas lidah dan putih pada lidah
    white_area = cv2.countNonZero(white_mask)
    tongue_area = cv2.countNonZero(tongue_mask)

    if tongue_area == 0:
        return {
            'success': False,
            'message': 'Lidah tidak terdeteksi'
        }

    white_area_percentage = (white_area / tongue_area) * 100

    return {
        'tongue_area': tongue_area,
        'white_area': white_area,
        'white_area_pertencage': white_area_percentage,
        'tongue_original': upload(cv2.imencode('.jpg', imgResult)[1].tobytes()),
        'full_tongue': upload(cv2.imencode('.jpg', tongue_mask)[1].tobytes()),
        'red_mask': upload(cv2.imencode('.jpg', red_mask)[1].tobytes()),
        'white_mask': upload(cv2.imencode('.jpg', white_mask)[1].tobytes())
    }

    # # Menampilkan hasil
    # print(f'Luas keseluruhan lidah: {tongue_area} piksel')
    # print(f"Luas area putih: {white_area} piksel")
    # print(f"Persentase area putih: {white_area_percentage:.2f}%")

    # if (white_area_percentage < 15):
    #     print('Lidah anda normal (tidak teridentifikasi warna putih)')
    # else:
    #     print('Lidah teridentifikasi warna putih')
    #     print('Periksa penyakit anda lebih lanjut')

def upload(file):
    r = requests.post(
        'https://pomf.lain.la/upload.php',
        files={'files[]': ("tes.jpg", file, "image/jpeg")}
    )

    return r.json()['files'][0]['url']

def detect_full_tongue(image):
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    lower_red1 = np.array([0, 70, 50])
    upper_red1 = np.array([5, 175, 255])

    lower_red2 = np.array([141, 68, 54])
    upper_red2 = np.array([178, 107, 255])

    lower_white = np.array([0, 0, 180])
    upper_white = np.array([180, 64, 255])

    # Buat mask untuk warna merah dan putih
    red_mask1 = cv2.inRange(hsv_image, lower_red1, upper_red1)
    red_mask2 = cv2.inRange(hsv_image, lower_red2, upper_red2)

    red_mask = cv2.bitwise_or(red_mask1, red_mask2)

    white_mask = cv2.inRange(hsv_image, lower_white, upper_white)

    # Gabungkan mask merah dan putih untuk mendapatkan keseluruhan lidah
    tongue_mask = cv2.bitwise_or(red_mask, white_mask)

    return red_mask, white_mask, tongue_mask

