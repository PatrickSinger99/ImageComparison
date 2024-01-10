from flask import Flask, request, jsonify
from flask_cors import CORS
from image_comparison import bytes_to_image
import cv2
import requests

app = Flask(__name__)
CORS(app)


@app.route('/compare', methods=['POST'])
def compare_img():
    content = request.get_json()
    src = content["src"]
    img = fetch_image(src)

    img = bytes_to_image(img)
    cv2.imshow("img", img)
    cv2.waitKey(0)


    return jsonify({'message': 'Image received'}), 200


def fetch_image(url):
    response = requests.get(url, stream=True)
    response.raise_for_status()
    return response.content


if __name__ == '__main__':
    app.run()
