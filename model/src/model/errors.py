from typing import ClassVar, override


class FacePipelineError(Exception):
    code: ClassVar[str] = "pipeline_error"
    status_code: ClassVar[int] = 500
    public_message: ClassVar[str] = "얼굴 분석 중 오류가 발생했습니다."

    @override
    def __str__(self) -> str:
        return self.public_message


class InvalidImageError(FacePipelineError):
    code: ClassVar[str] = "invalid_image"
    status_code: ClassVar[int] = 422
    public_message: ClassVar[str] = (
        "이미지 파일을 읽을 수 없습니다. JPG, PNG 또는 WebP 파일을 확인해 주세요."
    )


class UnsupportedMediaTypeError(FacePipelineError):
    code: ClassVar[str] = "unsupported_media_type"
    status_code: ClassVar[int] = 415
    public_message: ClassVar[str] = "JPG, PNG 또는 WebP 이미지만 사용할 수 있습니다."


class ImageTooLargeError(FacePipelineError):
    code: ClassVar[str] = "image_too_large"
    status_code: ClassVar[int] = 413
    public_message: ClassVar[str] = "이미지 크기는 10MB 이하여야 합니다."


class NoFaceError(FacePipelineError):
    code: ClassVar[str] = "no_face"
    status_code: ClassVar[int] = 422
    public_message: ClassVar[str] = (
        "얼굴을 찾지 못했습니다. 정면 얼굴이 선명하게 보이는 사진을 사용해 주세요."
    )


class MissingLandmarksError(FacePipelineError):
    code: ClassVar[str] = "missing_landmarks"
    status_code: ClassVar[int] = 422
    public_message: ClassVar[str] = "얼굴 정렬에 필요한 눈·코·입 위치를 찾지 못했습니다."


class ImageEncodingError(FacePipelineError):
    code: ClassVar[str] = "image_encoding_failed"
    public_message: ClassVar[str] = "분석 미리보기를 만들지 못했습니다."


class ModelInitializationError(FacePipelineError):
    code: ClassVar[str] = "model_initialization_failed"
    status_code: ClassVar[int] = 503
    public_message: ClassVar[str] = (
        "얼굴 분석 모델을 준비하지 못했습니다. 네트워크와 저장 공간을 확인해 주세요."
    )


class ModelInferenceError(FacePipelineError):
    code: ClassVar[str] = "model_inference_failed"
    status_code: ClassVar[int] = 500
    public_message: ClassVar[str] = "얼굴 모델이 이미지를 처리하지 못했습니다."


class EmptyEmbeddingsError(FacePipelineError):
    code: ClassVar[str] = "empty_embeddings"
    status_code: ClassVar[int] = 422
    public_message: ClassVar[str] = "평균을 계산할 기준 얼굴 벡터가 없습니다."


class NoReferenceIndexError(FacePipelineError):
    code: ClassVar[str] = "no_reference_index"
    status_code: ClassVar[int] = 409
    public_message: ClassVar[str] = "먼저 기준 인물 사진을 넣고 기준 벡터를 만들어 주세요."


class NoReferenceImagesError(FacePipelineError):
    code: ClassVar[str] = "no_reference_images"
    status_code: ClassVar[int] = 422
    public_message: ClassVar[str] = (
        "references 폴더에서 분석 가능한 기준 인물 사진을 찾지 못했습니다."
    )
