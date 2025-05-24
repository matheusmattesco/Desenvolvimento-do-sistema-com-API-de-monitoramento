import cv2
import mediapipe as mp
import numpy as np
from collections import defaultdict
import joblib
from django.conf import settings
import os

def extrair_keypoints_frame(frame, pose_model):
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose_model.process(img_rgb)

    if not results.pose_landmarks:
        return None

    keypoints = []
    for lm in results.pose_landmarks.landmark:
        keypoints.extend([lm.x, lm.y, lm.z])
    return np.array(keypoints).reshape(1, -1)


def analisar_posturas(video_path):
    caminho_modelo = os.path.join(settings.MEDIA_ROOT, 'modelo/modelo_ativo.pkl')
    modelo_completo = joblib.load(caminho_modelo)
    mlp = modelo_completo['modelo']
    scaler = modelo_completo['scaler']
    le = modelo_completo['label_encoder']

    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5)

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)

    contagem_posturas = defaultdict(int)
    total_frames = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        keypoints = extrair_keypoints_frame(frame, pose)
        if keypoints is not None:
            keypoints_norm = scaler.transform(keypoints)
            pred = mlp.predict(keypoints_norm)
            label_predita = le.inverse_transform(pred)[0]
            contagem_posturas[label_predita] += 1

        total_frames += 1

    cap.release()
    pose.close()

    duracao_posturas = {postura: frames / fps for postura, frames in contagem_posturas.items()}
    return duracao_posturas
