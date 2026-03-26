# chat-base-starter

[English](README.md) | [한국어](README.ko.md)

이 저장소는 `msa-base-starter`를 기반으로 AI 채팅을 추가할 수 있도록 확장한 포크 친화적 MSA 샘플입니다. 현재 active root는 브라우저용 chat relay와 내부 Aegra/LangGraph 런타임 구조를 보여줍니다.

## Active Architecture

```text
frontend (React/Vite, :3003)
  -> api-gateway (Spring Cloud Gateway, :8080)
    -> user-service (Spring Boot, auth/account)
    -> disclosure-service (FastAPI sample domain service)
    -> chat-service (FastAPI, browser-facing chat relay)
      -> aegra-service (Aegra/LangGraph agent runtime)
```

브라우저는 gateway만 호출합니다. `chat-service`는 conversation metadata와 사용자 소유권 검사를 담당하고, `aegra-service`는 내부 실행 엔진 역할만 맡습니다.

## 서비스별 환경 파일

각 서비스는 코드 옆에 자체 `.env.example` 파일을 둡니다.

```text
docker/postgres/.env.example
api-gateway/.env.example
user-service/.env.example
disclosure-service/.env.example
chat-service/.env.example
frontend/.env.example
aegra-service/.env.example
```

처음 실행 전에는 각각을 `.env`로 복사하세요.

```bash
cp docker/postgres/.env.example docker/postgres/.env
cp api-gateway/.env.example api-gateway/.env
cp user-service/.env.example user-service/.env
cp disclosure-service/.env.example disclosure-service/.env
cp chat-service/.env.example chat-service/.env
cp frontend/.env.example frontend/.env
cp aegra-service/.env.example aegra-service/.env
```

그 다음 `aegra-service/.env`에 실제 `OPENAI_API_KEY`를 넣으면 됩니다.

## 데이터베이스 구조

Python 서비스들은 여전히 하나의 Postgres 컨테이너를 공유하지만, 더 이상 하나의 논리 DB를 공유하지 않습니다.

- `disclosure-service` -> `disclosuredb`
- `chat-service` -> `chatdb`
- `aegra-service` -> `aegradb`

이 DB들은 `docker/postgres/.env` 값을 사용해서 `docker/postgres/init/01-init-multiple-dbs.sh`에서 초기화됩니다.

## 포트

외부 공개 엔트리포인트:

- Frontend: `http://localhost:3003`
- API Gateway: `http://localhost:8080`
- MySQL: `localhost:3307`
- Postgres: `localhost:5433`

기본적으로 내부 전용:

- `chat-service`
- `aegra-service`

이렇게 해서 gateway가 기본 브라우저 진입점이 되도록 유지합니다.

## Chat API Surface

`http://localhost:8080`의 gateway를 통해 노출됩니다.

- `GET /api/chat/conversations`
- `POST /api/chat/conversations`
- `GET /api/chat/conversations/{conversationId}`
- `POST /api/chat/conversations/{conversationId}/messages`

## Quick Start

### 1. 환경 파일 준비

각 `*.env.example` 파일을 `*.env`로 복사한 뒤, 로컬 환경에 맞게 값을 조정하세요.

최소 필수 변경:

- `aegra-service/.env` -> `OPENAI_API_KEY` 설정

### 2. 스택 실행

```bash
docker compose up -d
```

DB bootstrap 변수 변경이나 완전한 초기화가 필요하면:

```bash
docker compose down -v --remove-orphans
docker compose up -d
```

### 3. 접속

- Frontend: `http://localhost:3003`
- Gateway health: `http://localhost:8080/actuator/health`

## 데모용 단순화 선택 사항

이 저장소는 로컬 실행 속도를 위해 몇 가지 단순화를 유지합니다. 포크해서 실제 프로젝트 베이스로 쓸 팀은 아래 항목을 먼저 검토하는 편이 좋습니다.

- `frontend`는 데모 단순화를 위해 JWT를 `localStorage`에 저장합니다. 운영 환경에서는 보통 httpOnly cookie 또는 session 기반 전략이 더 적합합니다.
- `user-service`, `chat-service`는 startup 시 schema를 자동 생성/변경합니다. 운영 환경에서는 명시적인 migration 도구를 쓰는 편이 좋습니다.
- gateway와 downstream 서비스 간 신뢰는 forwarded identity header와 shared internal secret에 의존합니다. 운영에서는 downstream 비공개 네트워크와 더 강한 service-to-service trust를 함께 고려해야 합니다.
- disclosure 도메인 데이터는 원래 starter에서 온 샘플 콘텐츠라서, AI chat 아키텍처의 필수 요소가 아니라 optional reference code로 보는 편이 맞습니다.

## 검증 메모

로컬에서 확인한 항목:

- `docker compose config`
- `frontend/`에서 `npm run build`
- `chat-service/`에서 `python3 -m compileall app`
- `aegra-service/`에서 `python3 -m compileall src`
- `frontend`, `chat-service`, `aegra-service`, `api-gateway` Docker image build
- `http://localhost:8080` 기준 gateway 로그인 및 chat conversation/message flow
