import cv2
import torch
import numpy as np
from facenet_pytorch import MTCNN, InceptionResnetV1
from numpy.linalg import norm

# Load models
device = 'cuda' if torch.cuda.is_available() else 'cpu'
mtcnn = MTCNN(image_size=160, device=device)
facenet = InceptionResnetV1(pretrained='vggface2').eval().to(device)

# Load reference image
ref_img = cv2.imread("reference.jpg")
ref_rgb = cv2.cvtColor(ref_img, cv2.COLOR_BGR2RGB)
ref_face = mtcnn(ref_rgb)

ref_embedding = facenet(ref_face.unsqueeze(0).to(device)).detach().cpu().numpy()

# Webcam test
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face = mtcnn(rgb)

    if face is not None:
        emb = facenet(face.unsqueeze(0).to(device)).detach().cpu().numpy()
        similarity = np.dot(ref_embedding, emb.T) / (norm(ref_embedding) * norm(emb))
        cv2.putText(frame, f"Similarity: {similarity[0][0]:.2f}",
                    (20,40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

    cv2.imshow("Face Verification", frame)
    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()