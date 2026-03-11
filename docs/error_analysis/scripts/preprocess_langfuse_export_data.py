import json

import pandas as pd


def preprocess_langfuse_traces(filepath: str) -> pd.DataFrame:
    """Langfuse trace CSV 전처리 - 한글 디코딩 + 주요 필드 추출"""

    df = pd.read_csv(filepath)

    # JSON 파싱 헬퍼 (이중 인코딩 처리)
    def safe_json_loads(x):
        if pd.isna(x) or not x or x == "[]":
            return None
        try:
            parsed = json.loads(x)
            # 이중 인코딩된 경우 한 번 더 파싱
            if isinstance(parsed, str):
                parsed = json.loads(parsed)
            return parsed
        except Exception:
            return None

    # 1. input에서 마지막 human 메시지 추출
    def extract_input_message(x):
        parsed = safe_json_loads(x)
        if not parsed:
            return None
        messages = parsed.get("messages", [])
        human_msgs = [m["content"] for m in messages if m.get("type") == "human"]
        return human_msgs[-1] if human_msgs else None

    # 2. output에서 마지막 ai 메시지 추출
    def extract_output_message(x):
        parsed = safe_json_loads(x)
        if not parsed:
            return None
        messages = parsed.get("messages", [])
        ai_msgs = [m["content"] for m in messages if m.get("type") == "ai"]
        return ai_msgs[-1] if ai_msgs else None

    # 3. comments에서 content 추출 (여러 개면 | 로 연결)
    def extract_comments(x):
        parsed = safe_json_loads(x)
        if not parsed:
            return None
        return " | ".join([c["content"] for c in parsed if c.get("content")])

    # 4. tags 디코딩
    def decode_tags(x):
        parsed = safe_json_loads(x)
        if not parsed:
            return None
        return ", ".join(parsed) if isinstance(parsed, list) else str(parsed)

    # 컬럼 추가
    df["user_input"] = df["input"].apply(extract_input_message)
    df["ai_output"] = df["output"].apply(extract_output_message)
    df["comment_content"] = df["comments"].apply(extract_comments)
    df["tags_decoded"] = df["tags"].apply(decode_tags)

    # 원본 JSON 컬럼들도 디코딩 (스프레드시트용)
    for col in ["input", "output", "comments", "metadata"]:
        if col in df.columns:
            df[col] = df[col].apply(
                lambda x: json.dumps(safe_json_loads(x), ensure_ascii=False)
                if safe_json_loads(x)
                else x
            )

    return df


if __name__ == "__main__":
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser(
        description="Langfuse trace CSV 전처리 - 한글 디코딩 + 주요 필드 추출"
    )
    parser.add_argument("input", help="입력 CSV 파일 경로")
    parser.add_argument(
        "-o", "--output", help="출력 파일 경로 (기본: {입력파일명}_preprocessed.csv)"
    )

    args = parser.parse_args()

    input_path = Path(args.input)

    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.parent / f"{input_path.stem}_preprocessed.csv"

    df = preprocess_langfuse_traces(args.input)
    df.to_csv(output_path, index=False, encoding="utf-8-sig")

    print("✅ 전처리 완료!")
    print(f"📁 입력: {input_path}")
    print(f"📁 출력: {output_path}")
    print(f"📊 총 {len(df)}개 row")
    print("\n추가된 컬럼: user_input, ai_output, comment_content, tags_decoded")
