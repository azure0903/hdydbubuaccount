# 하늘꿈연동교회 부부청년부 회계관리

Next.js 16 App Router 기반 회계 앱입니다. `/bubu`는 부부청년부, `/dreamharam`은 꿈하람 유치부 회계 페이지입니다. 루트 `/`에서 부서를 선택합니다. 각 부서의 Sheet와 Supabase 거래·카테고리·명단은 분리됩니다. 기존 Google Sheet의 A:G 열은 거래 원본으로 유지하고, H열 `거래ID`에 거래별 UUID를 저장합니다.

## 시작하기

```bash
npm install
npm run dev
```

`.env`는 기존 Streamlit secrets에서 변환되어 있습니다. `GOOGLE_SERVICE_ACCOUNT_B64`와 `APP_USERS_B64`는 각각 서비스 계정 JSON과 기존 사용자 해시 JSON을 Base64로 담습니다. `SESSION_SECRET`은 서명된 로그인 쿠키에 쓰는 무작위 값입니다. 이 값들은 서버에서만 사용되며 Git에 포함하면 안 됩니다.

꿈하람 유치부는 아직 Sheet가 없으므로 `/dreamharam`에 접속하면 연결 안내가 표시되고 거래 저장은 비활성화됩니다. Sheet를 만든 뒤 기존 서비스 계정에 편집 권한을 주고 `.env`의 `DREAMHARAM_GOOGLE_SHEET_ID`에 ID를 넣으세요. 첫 행은 `기록일자, 회계일자, 입금, 입금내역, 출금, 출금내역, 작성자` 순서로 만듭니다. 빈 Sheet라면 앱이 헤더를 자동으로 만듭니다. 꿈하람 전용 로그인 계정을 쓰려면 `DREAMHARAM_USERS_B64`에 기존 `APP_USERS_B64`와 같은 구조의 사용자 해시 JSON을 Base64로 넣으세요. 비워두면 기존 계정을 공용으로 사용합니다. 로그인 세션은 부서별로 분리됩니다.

## Supabase 설정

1. Supabase 프로젝트를 만듭니다.
2. SQL Editor에서 [`supabase/schema.sql`](supabase/schema.sql)을 실행합니다. 이전 버전의 테이블이 있어도 다시 실행할 수 있으며, 기존 데이터는 부부청년부로 분류됩니다.
3. `.env`에 `SUPABASE_URL`과 **서버 전용** `SUPABASE_SECRET_KEY`를 입력합니다. 새로운 `sb_secret_...` 키 또는 레거시 `service_role` 키를 사용할 수 있습니다. 이 키는 브라우저에 노출되지 않습니다.
4. 개발 서버를 다시 시작합니다.

Supabase 설정 전에도 기존 Google Sheet의 거래 조회·입력·수정·삭제, CSV 다운로드를 사용할 수 있습니다. 카테고리와 명단 기능은 설정 후 활성화됩니다.

## Vercel 배포

1. 저장소를 Vercel에 연결하고 Framework Preset을 `Next.js`로 지정합니다.
2. `.env`의 필수 여섯 변수와 필요한 경우 꿈하람 설정 변수 두 개를 Vercel 프로젝트의 **Environment Variables**에 같은 이름으로 설정합니다. `.env` 파일 자체는 업로드하지 않습니다.
3. Supabase SQL을 적용하고 배포합니다. Build Command는 `npm run build`입니다.
4. 배포 후 로그인, 거래 조회, 거래 한 건 저장, 카테고리·명단 연결을 확인합니다.

최초 거래 조회 때 기존 Sheet 행의 H열에 UUID를 채웁니다. 기존 A:G 값은 변경하지 않습니다. Sheet에 새 행을 직접 추가하면 다음 조회 때 H열에 UUID를 채우고 Supabase에 사본을 동기화합니다. Sheet에서 직접 행을 삭제한 경우도 다음 조회 때 Supabase의 이전 사본을 정리합니다. 두 저장소 간 원자적 트랜잭션은 없으므로 Supabase 동기화 실패 시 Sheet 저장 결과와 경고를 화면에 표시합니다.

## 기능

- 기존 계정 로그인 및 서버 서명 쿠키
- 입금/출금 전환 입력, 거래 수정·삭제
- 카테고리 추가·수정·삭제, 입금/출금 유형 및 색상 설정
- 명단 추가·수정·삭제, 활성 상태 및 메모 관리
- 월·유형·카테고리·명단·문자 검색, 필터된 합계
- UTF-8 CSV 다운로드
