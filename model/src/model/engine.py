from base64 import b64encode
from dataclasses import dataclass
from typing import Final, Protocol, final

import cv2
import numpy as np
from numpy.typing import NDArray
from uniface.detection import YOLOv8Face
from uniface.face_utils import face_alignment
from uniface.parsing import BiSeNet
from uniface.recognition import ArcFace
from uniface.types import Face

from model.errors import (
    ImageEncodingError,
    InvalidImageError,
    ModelInferenceError,
    ModelInitializationError,
    NoFaceError,
)
from model.masking import apply_identity_mask, build_identity_mask
from model.similarity import Embedding, normalize_embedding

type ImageArray = NDArray[np.uint8]

_DETECTION_CONFIDENCE_WARNING: Final = 0.75
_SMALL_FACE_RATIO: Final = 0.22
_POSE_OFFSET_RATIO: Final = 0.18
_PREVIEW_MAX_SIDE: Final = 960
_LANDMARK_COLOR: Final = (148, 230, 49)


@dataclass(frozen=True, slots=True)
class ProcessedFace:
    embedding: Embedding
    confidence: float
    warnings: tuple[str, ...]
    original: str
    detected: str
    aligned: str
    masked: str


class FaceEngine(Protocol):
    def process(self, image_bytes: bytes) -> ProcessedFace: ...


@final
class UniFaceEngine:
    def __init__(self) -> None:
        try:
            self._detector: YOLOv8Face = YOLOv8Face(providers=["CPUExecutionProvider"])
            self._parser: BiSeNet = BiSeNet(providers=["CPUExecutionProvider"])
            self._recognizer: ArcFace = ArcFace(providers=["CPUExecutionProvider"])
        except (OSError, RuntimeError, ValueError) as error:
            raise ModelInitializationError from error

    def process(self, image_bytes: bytes) -> ProcessedFace:
        image = _decode_image(image_bytes)
        try:
            faces = tuple(self._detector.detect(image))
            face = _select_face(faces)
            landmarks = _landmarks(face)
            aligned, _ = face_alignment(image, landmarks, image_size=112)
            labels = self._parser.parse(aligned)
            identity_mask = build_identity_mask(labels)
            masked = apply_identity_mask(aligned, identity_mask)
            embedding = normalize_embedding(
                np.asarray(self._recognizer.get_embedding(masked).ravel(), dtype=np.float32)
            )
        except NoFaceError:
            raise
        except (cv2.error, RuntimeError, ValueError) as error:
            raise ModelInferenceError from error

        detected = _draw_detection(image, face)
        return ProcessedFace(
            embedding=embedding,
            confidence=float(face.confidence),
            warnings=_quality_warnings(face, (image.shape[0], image.shape[1]), len(faces)),
            original=_encode_preview(image),
            detected=_encode_preview(detected),
            aligned=_encode_preview(aligned),
            masked=_encode_preview(masked),
        )


def _decode_image(image_bytes: bytes) -> ImageArray:
    encoded = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
    if image is None:
        raise InvalidImageError
    return np.asarray(image, dtype=np.uint8)


def _face_area(face: Face) -> float:
    x1, y1, x2, y2 = (float(value) for value in _bbox(face))
    return max(0.0, x2 - x1) * max(0.0, y2 - y1)


def _select_face(faces: tuple[Face, ...]) -> Face:
    if not faces:
        raise NoFaceError
    return max(faces, key=_face_area)


def _bbox(face: Face) -> NDArray[np.float32]:
    bbox: NDArray[np.float32] = face.bbox
    return bbox[:4]


def _landmarks(face: Face) -> NDArray[np.float32]:
    landmarks: NDArray[np.float32] = face.landmarks
    return landmarks


def _draw_detection(image: ImageArray, face: Face) -> ImageArray:
    output = image.copy()
    x1, y1, x2, y2 = (round(float(value)) for value in _bbox(face))
    _ = cv2.rectangle(output, (x1, y1), (x2, y2), _LANDMARK_COLOR, thickness=3)
    for point in _landmarks(face):
        x, y = round(float(point[0])), round(float(point[1]))
        _ = cv2.circle(output, (x, y), radius=5, color=_LANDMARK_COLOR, thickness=-1)
    return output


def _quality_warnings(
    face: Face,
    image_shape: tuple[int, ...],
    detected_count: int,
) -> tuple[str, ...]:
    warnings: list[str] = []
    if detected_count > 1:
        warnings.append("여러 얼굴 중 가장 큰 얼굴을 분석했습니다.")
    if face.confidence < _DETECTION_CONFIDENCE_WARNING:
        warnings.append("얼굴 검출 신뢰도가 낮아 결과가 흔들릴 수 있습니다.")
    x1, y1, x2, y2 = (float(value) for value in _bbox(face))
    if min(x2 - x1, y2 - y1) < min(image_shape) * _SMALL_FACE_RATIO:
        warnings.append("얼굴 영역이 작습니다. 더 가까이 촬영한 사진이 좋습니다.")
    landmarks = _landmarks(face)
    eyes = landmarks[:2]
    eye_distance = float(np.linalg.norm(eyes[1] - eyes[0]))
    nose_offset = abs(float(landmarks[2, 0] - float(np.mean(eyes[:, 0]))))
    if eye_distance > 0.0 and nose_offset / eye_distance > _POSE_OFFSET_RATIO:
        warnings.append("얼굴 각도가 큽니다. 정면 사진에서 결과가 더 안정적입니다.")
    return tuple(warnings)


def _encode_preview(image: ImageArray) -> str:
    height: int = image.shape[0]
    width: int = image.shape[1]
    longest = max(height, width)
    preview = image
    if longest > _PREVIEW_MAX_SIDE:
        scale = _PREVIEW_MAX_SIDE / longest
        preview = cv2.resize(image, (round(width * scale), round(height * scale)))
    success, encoded = cv2.imencode(".webp", preview, [cv2.IMWRITE_WEBP_QUALITY, 88])
    if not success:
        raise ImageEncodingError
    return f"data:image/webp;base64,{b64encode(encoded.tobytes()).decode('ascii')}"
