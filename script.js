const urlInput = document.getElementById('urlInput');
const analyzeBtn = document.getElementById('analyzeBtn');
const resultBox = document.getElementById('result');

function getLevenshteinDistance(a, b) {
  const matrix = Array.from({ length: a.length + 1 }, () => Array(b.length + 1).fill(0));
  for (let i = 0; i <= a.length; i++) matrix[i][0] = i;
  for (let j = 0; j <= b.length; j++) matrix[0][j] = j;

  for (let i = 1; i <= a.length; i++) {
    for (let j = 1; j <= b.length; j++) {
      const cost = a[i - 1] === b[j - 1] ? 0 : 1;
      matrix[i][j] = Math.min(
        matrix[i - 1][j] + 1,
        matrix[i][j - 1] + 1,
        matrix[i - 1][j - 1] + cost
      );
    }
  }
  return matrix[a.length][b.length];
}

const TARGET_BRANDS = [
  { name: 'naver', domain: 'naver.com' },
  { name: 'kakao', domain: 'kakao.com' },
  { name: 'daum', domain: 'daum.net' },
  { name: 'google', domain: 'google.com' },
  { name: 'coupang', domain: 'coupang.com' },
  { name: 'facebook', domain: 'facebook.com' },
  { name: 'apple', domain: 'apple.com' },
  { name: 'paypal', domain: 'paypal.com' },
  { name: 'toss', domain: 'toss.im' }
];

function analyzeUrl(rawUrl) {
  const urlStr = rawUrl.trim();
  const indicators = [];
  let score = 0;

  if (!urlStr) {
    return {
      label: '입력 필요',
      message: 'URL을 입력해 주세요.',
      score: 0,
      indicators: []
    };
  }

  let parsedUrl;
  try {
    const validProtocolUrl = /^https?:\/\//i.test(urlStr) ? urlStr : `http://${urlStr}`;
    parsedUrl = new URL(validProtocolUrl);
  } catch (e) {
    return {
      label: 'URL 형식 오류',
      message: '❌ 올바르지 않은 URL 형식입니다.',
      score: 10,
      indicators: ['URL 파싱 실패 (주소 형식이 잘못됨)']
    };
  }

  const hostname = parsedUrl.hostname.toLowerCase();

  const hasTldInSubdomain = /^.+?\.(com|net|org|co\.kr|io)\./i.test(hostname);
  if (hasTldInSubdomain) {
    indicators.push('🚨 서브도메인 위장: 주소 중간에 .com 등의 도메인 형식을 포함하여 정식 사이트처럼 위장했습니다.');
    score += 7;
  }

  if (/^\d{1,3}(\.\d{1,3}){3}$/.test(hostname)) {
    indicators.push('IP 주소 형태로 직접 접속 중입니다.');
    score += 5;
  }

  if (parsedUrl.protocol !== 'https:') {
    indicators.push('보안 연결(HTTPS)이 적용되지 않은 HTTP 주소입니다.');
    score += 2;
  }

  let isOfficialDomain = false;
  const domainParts = hostname.split('.');
  const sld = domainParts.length >= 2 ? domainParts[domainParts.length - 2] : hostname;

  for (const brand of TARGET_BRANDS) {
    if (hostname === brand.domain || hostname.endsWith('.' + brand.domain)) {
      isOfficialDomain = true;
      break;
    }

    if (hostname.includes(brand.domain) && !hostname.endsWith('.' + brand.domain)) {
      indicators.push(`🚨 서브도메인 위장: 정식 도메인(${brand.domain})을 앞쪽에 배치하여 착시를 유도했습니다.`);
      score += 8;
      break;
    }

    if (sld.includes(brand.name) && sld !== brand.name) {
      indicators.push(`⚠️ 브랜드 명칭 남용: 공식 브랜드명(${brand.name}) 뒤에 다른 단어가 결합된 도메인입니다.`);
      score += 6;
      break;
    }

    const distance = getLevenshteinDistance(sld, brand.name);
    if (distance > 0 && distance <= 2 && sld.length >= 3) {
      indicators.push(`⚠️ 철자 변형(타이포스쿼팅) 감지: '${brand.name}' 브랜드와 매우 유사한 철자('${sld}')입니다.`);
      score += 7;
      break;
    }
  }

  if (isOfficialDomain) {
    return {
      label: '공식 사이트',
      message: '✅ 검증된 브랜드의 공식 사이트입니다.',
      score: 0,
      indicators: ['공식 화이트리스트 도메인 일치']
    };
  }

  const suspiciousWords = ['login', 'verify', 'secure', 'update', 'confirm', 'account', 'bank', 'pay', 'gift', 'free'];
  const matchedWords = suspiciousWords.filter((word) => parsedUrl.href.toLowerCase().includes(word));
  if (matchedWords.length) {
    indicators.push(`의심 키워드 포함: ${matchedWords.join(', ')}`);
    score += Math.min(3, matchedWords.length);
  }

  if (['bit.ly', 't.co', 'tinyurl.com', 'me2.do'].some((shortener) => hostname.includes(shortener))) {
    indicators.push('URL 단축 서비스가 사용되었습니다.');
    score += 3;
  }

  if (hostname.includes('--') || hostname.includes('__')) {
    indicators.push('도메인에 비정상적인 연속 기호가 포함되어 있습니다.');
    score += 2;
  }

  let label = '안전한 사이트로 보입니다';
  let emoji = '✅';
  if (score >= 7) {
    label = '피싱 사이트일 가능성이 매우 높습니다';
    emoji = '🚨';
  } else if (score >= 3) {
    label = '의심스러운 요소가 발견되었습니다';
    emoji = '⚠️';
  }

  return {
    label,
    message: `${emoji} ${label}`,
    score,
    indicators
  };
}

function renderResult(result) {
  const lines = [];
  lines.push(`<strong>${result.message}</strong>`);
  lines.push('<br><small>※ 본 도구는 자동 탐지용이며, 실제 접속 시 주소창의 정확한 철자를 직접 재확인하세요.</small>');
  resultBox.innerHTML = lines.join('<br>');
}

analyzeBtn.addEventListener('click', () => {
  const result = analyzeUrl(urlInput.value);
  renderResult(result);
});

urlInput.addEventListener('keydown', (event) => {
  if (event.key === 'Enter') {
    const result = analyzeUrl(urlInput.value);
    renderResult(result);
  }
});
