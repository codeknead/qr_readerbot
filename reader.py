import cv2
import io
from PIL import Image, ImageDraw
from pyzbar.pyzbar import decode
from pyzbar.wrapper import ZBarSymbol


def reader(image):
    img = cv2.imread(image)
    barcodes = decode(img)
    text = ''
    for barcode in barcodes:
        (x, y, w, h) = barcode.rect
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
        barcodeData = barcode.data.decode("utf-8")
        barcodeType = barcode.type
        text = "{} ({})".format(barcodeData, barcodeType)

    return text


def select_code_on_image(image, polygon):
    coordinates = [(p.x, p.y) for p in polygon]
    coordinates.append(coordinates[0])
    image = image.convert(mode='RGB')
    draw = ImageDraw.Draw(image)
    draw.line(coordinates, fill='#00aa00', width=4)

    return image


def decode_and_select(image_file):
    decoded_text = None
    image = Image.open(image_file)

    img = cv2.imread(image_file)
    mask = cv2.inRange(img, (0, 0, 0), (200, 200, 200))
    thresholded = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    inverted = 255 - thresholded  # black-in-white
    cv2.imwrite("IMGInverted.jpg", inverted)

    results = decode(inverted, symbols=[ZBarSymbol.QRCODE])

    if results:
        decoded_text = []
        for result in results:
            image = select_code_on_image(image, result.polygon)
            decoded_text.append(result.data.decode())

        new_image_file = io.BytesIO()
        image.save(new_image_file, format='PNG')
        new_image_file.seek(0)
        decoded_text = '\n'.join(decoded_text)

    if decoded_text:
        return decoded_text
    return 'QR code not found.'
