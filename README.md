# 피싱 사이트 구분 도우미

이 프로젝트는 URL을 입력해 피싱 사이트 의심 여부를 간단히 확인할 수 있는 웹 기반 도구입니다.

## 포함된 파일
- `index.html`: 정적 웹 페이지 진입점
- `styles.css`: 스타일 시트
- `script.js`: URL 분석 로직
- `app.py`: Streamlit 기반 실행 파일
- `requirements.txt`: Streamlit 의존성

## 기능
- URL 입력 후 분석 실행
- HTTPS, IP 주소, 의심 키워드, 유사 도메인 패턴 확인
- 간단한 판단 결과 표시

## 실행 방법

### 1) 정적 웹 페이지로 실행
```bash
python -m http.server 8000
```
브라우저에서 아래 주소로 접속합니다.
```text
http://127.0.0.1:8000/
```

### 2) Streamlit으로 실행
```bash
pip install -r requirements.txt
streamlit run app.py
```
브라우저에서 아래 주소로 접속합니다.
```text
http://localhost:8501
```

## 참고
- 이 도구는 교육용/실험용으로 만든 간단한 판별 도구입니다.
- 실제 사이트 안전 여부를 완전히 보장하지는 않습니다.
