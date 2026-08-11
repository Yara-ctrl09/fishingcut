import streamlit as st

st.set_page_config(page_title="피싱 사이트 구분 도우미", page_icon="🛡️", layout="centered")
st.title("피싱 사이트 구분 도우미")
st.write("입력한 URL을 간단히 분석해 피싱 사이트 의심 여부를 확인해 보세요.")

url = st.text_input("URL 입력", placeholder="예: https://www.naver.com")

if st.button("분석하기"):
    if not url.strip():
        st.warning("URL을 입력해 주세요.")
    else:
        normalized = url.strip().lower()
        score = 0
        reasons = []

        if not url.startswith("http://") and not url.startswith("https://"):
            reasons.append("URL 형식이 명확하지 않습니다.")
            score += 2

        if not normalized.startswith("https://"):
            reasons.append("HTTPS가 적용되지 않았습니다.")
            score += 2

        if normalized.startswith("www."):
            reasons.append("www.로 시작하는 주소는 일반적으로 안전한 형태로 간주됩니다.")

        suspicious_words = ["login", "verify", "secure", "update", "confirm", "account", "bank", "pay", "gift", "free"]
        matched = [w for w in suspicious_words if w in normalized]
        if matched:
            reasons.append(f"의심 키워드 포함: {', '.join(matched)}")
            score += len(matched)

        if any(token in normalized for token in ["bit.ly", "t.co", "tinyurl.com", "me2.do"]):
            reasons.append("단축 URL이 사용되었습니다.")
            score += 3

        if score >= 5:
            st.error("피싱 사이트일 가능성이 높습니다")
        else:
            st.success("안전한 사이트로 보입니다")

        if reasons:
            st.write("### 확인된 항목")
            for item in reasons:
                st.write(f"- {item}")
        else:
            st.write("특별한 의심 신호는 발견되지 않았습니다.")
