import os

from nudenet import NudeClassifierLite, NudeClassifier
import cv2

classifier = NudeClassifierLite()
video_classifier = NudeClassifier()

def is_images_nsfw(images):
    is_nsfw = 0
    for image in images:
        try:
            path = 'images/' + image
            predict = classifier.classify(path)
            is_nsfw += predict[path]['unsafe'] > predict[path]['safe']
            os.remove(path)
        except Exception as e:
            print(e)
    return is_nsfw


def is_gif_nsfw(videos):
    is_nsfw = 0
    for video in videos:
        try:
            path = video
            os.environ['SKIP_N_FRAMES'] = "0"
            predict = video_classifier.classify_video(path, batch_size=1)
            print(predict)
            for pred_idx, pred in predict['preds'].items():
                is_nsfw += (pred['unsafe'] > pred['safe'])
            os.remove(path)
        except Exception as e:
            print(e)
    return is_nsfw


def is_video_nsfw(videos):
    is_nsfw = 0
    for video in videos:
        try:
            path = video
            os.environ['SKIP_N_FRAMES'] = "0.5"
            predict = video_classifier.classify_video(path, batch_size=4)
            print(predict)
            for pred_idx, pred in predict['preds'].items():
                is_nsfw += (pred['unsafe'] > pred['safe'])
            os.remove(path)
        except Exception as e:
            print(e)
    return is_nsfw


#print(is_gif_nsfw(['sticker.webm']))



