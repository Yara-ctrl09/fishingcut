import re
from urllib.parse import urlsplit

import streamlit as st


def get_levenshtein_distance(a: str, b: str) -> int:
    matrix = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a) + 1):
        matrix[i][0] = i
    for j in range(len(b) + 1):
        matrix[0][j] = j

    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            matrix[i][j] = min(
                matrix[i - 1][j] + 1,
                matrix[i][j - 1] + 1,
                matrix[i - 1][j - 1] + cost,
            )
    return matrix[len(a)][len(b)]


def analyze_url(raw_url: str):
    url = raw_url.strip()
    reasons = []
    score = 0

    if not url:
        return {
            "label": "입력 필요",
            "message": "URL을 입력해 주세요.",
            "score": 0,
            "reasons": [],
        }

    if not re.match(r"^https?://", url):
        url = f"http://{url}"

    try:
        parsed = urlsplit(url)
    except ValueError:
        return {
            "label": "URL 형식 오류",
            "message": "올바르지 않은 URL 형식입니다.",
            "score": 10,
            "reasons": ["URL 파싱 실패"],
        }

    hostname = (parsed.hostname or "").lower()
    if not hostname:
        return {
            "label": "URL 형식 오류",
            "message": "올바르지 않은 URL 형식입니다.",
            "score": 10,
            "reasons": ["호스트 이름이 없습니다."],
        }

    if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", hostname):
        reasons.append("IP 주소 형태로 접속 중입니다.")
        score += 5

    if parsed.scheme != "https":
        reasons.append("HTTPS가 적용되지 않았습니다.")
        score += 3

    if re.search(r"^.+\.(com|net|org|co\.kr|io)\.", hostname):
        reasons.append("서브도메인 위장 패턴이 감지되었습니다.")
        score += 7

    official_domains = {
        "naver": "naver.com",
        "kakao": "kakao.com",
        "daum": "daum.net",
        "google": "google.com",
        "coupang": "coupang.com",
        "facebook": "facebook.com",
        "apple": "apple.com",
        "paypal": "paypal.com",
        "toss": "toss.im",
    }

    is_official = any(
        hostname == domain or hostname.endswith(f".{domain}")
        for domain in official_domains.values()
    )
    if is_official:
        return {
            "label": "안전한 사이트로 보입니다",
            "message": "공식 도메인으로 확인되었습니다.",
            "score": 0,
            "reasons": ["공식 도메인입니다."],
        }

    suspicious_words = [
        "login",
        "verify",
        "secure",
        "update",
        "confirm",
        "account",
        "bank",
        "pay",
        "gift",
        "free",
        "prize",
    ]
    matched_words = [
        word for word in suspicious_words if word in hostname or word in parsed.path.lower() or word in parsed.query.lower()
    ]
    if matched_words:
        reasons.append(f"의심 키워드 포함: {', '.join(matched_words)}")
        score += len(matched_words) * 2

    if any(token in hostname for token in ["bit.ly", "t.co", "tinyurl.com", "me2.do"]):
        reasons.append("단축 URL이 사용되었습니다.")
        score += 3

    if "--" in hostname or "__" in hostname:
        reasons.append("비정상적인 기호가 포함되어 있습니다.")
        score += 2

    sld = hostname.split(".")[0] if hostname else hostname
    for brand, domain in official_domains.items():
        if brand in hostname and hostname != domain and not hostname.endswith(f".{domain}"):
            reasons.append(f"브랜드명({brand})과 유사한 도메인 패턴이 감지되었습니다.")
            score += 4
            break

        distance = get_levenshtein_distance(sld, brand)
        if distance > 0 and distance <= 2 and len(sld) >= 3:
            reasons.append(f"철자 유사도 감지: {brand}와 비슷한 형태입니다.")
            score += 5
            break

    if score >= 7:
        label = "피싱 사이트일 가능성이 높습니다"
        message = "의심스러운 패턴이 확인되었습니다."
    elif score >= 3:
        label = "의심스러운 요소가 발견되었습니다"
        message = "주의가 필요합니다."
    else:
        label = "안전한 사이트로 보입니다"
        message = "특별한 의심 신호는 발견되지 않았습니다."

    return {
        "label": label,
        "message": message,
        "score": score,
        "reasons": reasons,
    }


def main():
    st.set_page_config(page_title="피싱 사이트 구분 도우미", page_icon="🛡️", layout="centered")
    st.title("피싱 사이트 구분 도우미")
    st.write("입력한 URL을 분석해 피싱 사이트 의심 여부를 확인해 보세요.")

    url = st.text_input("URL 입력", placeholder="예: https://www.naver.com")

    if st.button("분석하기"):
        if not url.strip():
            st.warning("URL을 입력해 주세요.")
            return

        result = analyze_url(url)
        if result["label"] == "피싱 사이트일 가능성이 높습니다":
            st.error(result["message"])
        elif result["label"] == "의심스러운 요소가 발견되었습니다":
            st.warning(result["message"])
        else:
            st.success(result["message"])

        if result["reasons"]:
            st.write("### 확인된 항목")
            for item in result["reasons"]:
                st.write(f"- {item}")


if __name__ == "__main__":
    main()
